"""Local data storage."""

import logging
import re
import subprocess
from abc import ABC, abstractmethod
from functools import singledispatchmethod
from pathlib import Path
from typing import TYPE_CHECKING, List, Literal, Mapping, Set, Tuple, Union

import click
import packaging.version
import sdmx
import sdmx.model.v21 as m
import sdmx.urn
from sdmx.message import StructureMessage

from transport_data.util.sdmx import anno_generated

if TYPE_CHECKING:
    import transport_data.config

log = logging.getLogger(__name__)


def _full_urn(value: str) -> str:
    """Convert possibly partial `value` to a complete SDMX URN."""
    urn_base = "urn:sdmx:org.sdmx.infomodel."
    if value.startswith(urn_base):
        return value
    else:
        return f"{urn_base}package.{value}"


_SHORT_URN_EXPR = re.compile(r"(urn:sdmx:org\.sdmx\.infomodel\.[^\.]+\.)?(?P<short>.*)")


def _short_urn(value: str) -> str:
    m = _SHORT_URN_EXPR.match(value)
    assert m
    return m.group("short")


def _maintainer(obj: Union[m.MaintainableArtefact, m.DataSet]) -> m.Agency:
    """Return a maintainer for `obj`.

    If `obj` is :class:`.DataSet`, the maintainer of the data flow is used.
    """
    if isinstance(obj, m.MaintainableArtefact):
        return obj.maintainer
    else:
        assert obj.described_by
        return obj.described_by.maintainer


class BaseStore(ABC):
    """A class for file-based storage of SDMX artefacts."""

    #: Top level file system path containing stored files.
    path: Path

    @abstractmethod
    def __init__(self, config: "transport_data.config.Config") -> None: ...

    def get(self, urn: str) -> object:
        """Retrieve an object given its full or partial `urn`."""
        # Identify the path to the object
        urn = _full_urn(urn)
        path = self.path_for(urn)
        assert path.exists(), f"No object {path}"

        # Read an SDMX Message from the path
        msg = sdmx.read_sdmx(path)

        # Extract the object
        m = sdmx.urn.match(urn)
        result = msg.get(m["id"])
        assert result

        return result

    def list(self, maintainer_id: str) -> List[str]:
        """Return a list of URNs for objects with `maintainer_id`."""
        base = self.path.joinpath(maintainer_id)
        result: Set[str] = set()
        for path in sorted(base.glob("*.xml")):
            msg = sdmx.read_sdmx(path)
            for _, cls in msg.iter_collections():
                result.update(_short_urn(obj.urn) for obj in msg.objects(cls).values())

        return sorted(result)

    @singledispatchmethod
    def path_for(self, obj: m.MaintainableArtefact) -> Path:
        """Determine a path and filename for `obj`."""
        return self.path.joinpath(
            obj.maintainer.id, f"{obj.__class__.__name__}_{obj.maintainer.id}_{obj.id}"
        ).with_suffix(".xml")

    @path_for.register
    def _(self, obj: m.DataSet) -> Path:
        """Determine a path and filename for `obj`."""
        # Generate a path for the data set's corresponding data flow
        tmp = self.path_for(obj.described_by)
        return tmp.with_name(tmp.name.replace("DataflowDefinition", "DataSet"))

    @path_for.register
    def _(self, urn: str) -> Path:
        """Generate a Path given a `urn`."""
        m = sdmx.urn.match(_full_urn(urn))
        return self.path.joinpath(
            m["agency"], "_".join([m["class"], m["agency"], m["id"]])
        ).with_suffix(".xml")

    def setdefault(self, default: m.MaintainableArtefact) -> m.MaintainableArtefact:
        """If an object with the URN of `default` is in the registry, return it.

        Otherwise, :meth:`.write` `default`.
        """
        try:
            # Existing object
            return self.get(sdmx.urn.make(default))
        except AssertionError:
            self.write(default)
            return default

    @singledispatchmethod
    def write(
        self,
        obj: Union[m.MaintainableArtefact, m.DataSet],
        *,
        annotate: bool = True,
        **kwargs,
    ) -> Path:
        """Write `obj` into the registry as SDMX-ML.

        The path and filename are determined by the object properties.
        """
        if len(kwargs):
            raise TypeError(f"Extra keyword arguments: {kwargs}")

        path = self.path_for(obj)

        # Make the parent directory (but not multiple parents)
        path.parent.mkdir(exist_ok=True)

        if isinstance(obj, m.AnnotableArtefact) and annotate:
            # Annotate the object with information about how it was generated
            # TODO don't do this for files retrieved directly from an SDMX API
            anno_generated(obj)

        if isinstance(obj, m.MaintainableArtefact):
            # Encapsulate in a StructureMessage
            sm = sdmx.message.StructureMessage()
            sm.add(obj)
            msg: sdmx.message.Message = sm
        else:
            dm = sdmx.message.DataMessage()
            dm.data.append(obj)
            msg = dm

        with open(path, "wb") as f:
            f.write(sdmx.to_xml(msg, pretty_print=True))

        log.info(f"Wrote {path}")

        if isinstance(obj, m.DataSet):
            csv_path = path.with_suffix(".csv")
            sdmx.to_csv(obj, path=csv_path, attributes="gso")
            log.info(f"Wrote {csv_path}")

        return path

    @write.register
    def _write_structuremessage(self, obj: StructureMessage, **kwargs):
        # Write each of the structure objects a separate file
        for kind in ("codelist", "concept_scheme", "dataflow", "structure"):
            for obj_ in getattr(obj, kind).values():
                self.write(obj_, **kwargs)

    def assign_version(
        self,
        obj: m.MaintainableArtefact,
        default="0.0.0",
        increment: Union[bool, Tuple[bool, bool, bool]] = False,
    ) -> None:
        """Assign a version to `obj`.

        If `increment` is :data:`False`, the version will be the latest already existing
        in the registry, if any, or `default` if no version of `obj` is stored.

        Otherwise, `increment` should be a 3-tuple of :class:`bool`, which are passed as
        arguments to :func:`next_version`.
        """
        if increment is False:
            obj.version = (self.list_versions(obj) or [default])[-1]
        else:
            if not isinstance(increment, tuple):
                increment = (increment, False, False)
            obj.version = self.next_version(obj, *increment)

    def list_versions(self, obj: m.MaintainableArtefact) -> List[str]:
        """List all versions of `obj` already stored in the registry."""

        # Path that would result from writing `obj`
        path = self.path_for(obj)

        if not path.exists():
            return []

        # Read an SDMX Message from the path
        msg = sdmx.read_sdmx(path)

        # Iterate over objects
        versions = set()
        for _, cls in msg.iter_collections():
            for obj in msg.objects(cls).values():
                versions.add(obj.version)

        return sorted(versions)

    def next_version(
        self, obj: m.MaintainableArtefact, major=False, minor=True, patch=False
    ) -> str:
        """Return an incremented version string for `obj`."""
        v = packaging.version.parse(self.list_versions(obj)[-1])
        return f"{v.major + int(major)}.{v.minor + int(minor)}.{v.micro + int(patch)}"


class LocalStore(BaseStore):
    """Unversioned local storage."""

    def __init__(self, config) -> None:
        self.path = config.data_path.joinpath("local")
        self.path.mkdir(parents=True, exist_ok=True)


class Registry(BaseStore):
    """Registry of TDCI-maintained structure information.

    Currently these are stored in, and available from, the
    `transport-data/registry <https://github.com/transport-data/registry>`_ GitHub
    repository. This class handles the interaction with a local clone of that
    repository.

    In the future, they will be maintained on a full SDMX REST web service, and this
    class will handle retrieving from and publishing to that web service, with
    appropriate caching etc.
    """

    def __init__(self, config) -> None:
        self.path = config.data_path.joinpath("registry")
        if not self.path.exists():
            print(f"WARNING: TDC registry not existing in {self.path}")
            print("To clone, run: tdc registry clone")

    def _gh(self, *parts):
        """Invoke `gh`, the GitHub CLI client."""
        return subprocess.run(("gh",) + parts)

    def _git(self, *parts):
        """Invoke `git` in the :attr:`path` directory."""
        return subprocess.run(("git", "-C", str(self.path)) + parts)

    def clone(self):
        """Clone the repository."""
        self._gh("repo", "clone", "transport-data/registry", str(self.path))

    @singledispatchmethod
    def write(
        self,
        obj: Union[m.MaintainableArtefact, m.DataSet],
        *,
        annotate: bool = True,
        **kwargs,
    ) -> Path:
        """Write `obj` into the registry as SDMX-ML."""
        show_status = kwargs.pop("_show_status", False)
        result = super().write(obj, annotate=annotate, **kwargs)

        # Add to git, but do not commit
        # NB if the path is specifically covered by a .gitignore entry, this will generate
        #    some advice messages but have no effect. See e.g. registry/ESTAT/README.
        # TODO ignore "The following paths are ignored by one of your .gitignore files"
        self._git("add", str(result.relative_to(self.path)))
        if show_status:
            self._git("status")

        return result

    write.register(BaseStore._write_structuremessage)


class UnionStore(BaseStore):
    """A store that maps between a :class:`.LocalStore` and :class:`.Registry`."""

    #: Instances of :class:`.LocalStore` and :class:`.Registry`.
    store: Mapping[Literal["local", "registry"], BaseStore]

    #: Mapping from maintainer IDs (such as "TEST" or "TDCI") to either "local" or
    #: "registry".
    map: Mapping[str, Literal["local", "registry"]]

    def __init__(self, config) -> None:
        self.store = dict(local=LocalStore(config), registry=Registry(config))
        self.map = config.store_map

    def _get_store(self, obj: m.MaintainableArtefact) -> BaseStore:
        """Return the store that wants to handle `obj`."""
        return self.store[self.map.get(_maintainer(obj).id, "local")]

    def get(self, urn: str) -> object:
        """Retrieve an object given its full or partial `urn`."""
        # Identify the path to the object
        urn = _full_urn(urn)
        m = sdmx.urn.match(urn)

        return self.store[self.map.get(m["agency"], "local")].get(urn)

    def list(self, maintainer_id: str):
        return sorted(
            set(self.store["registry"].list(maintainer_id))
            | set(self.store["local"].list(maintainer_id))
        )

    @singledispatchmethod
    def write(
        self,
        obj: Union[m.MaintainableArtefact, m.DataSet],
        *,
        annotate: bool = True,
        **kwargs,
    ) -> Path:
        """Write `obj` into the registry as SDMX-ML."""
        return self._get_store(obj).write(obj, annotate=annotate, **kwargs)

    write.register(BaseStore._write_structuremessage)

    def assign_version(
        self, obj: m.MaintainableArtefact, default="0.0.0", increment=False
    ):
        return self._get_store(obj).assign_version(
            obj, default=default, increment=increment
        )

    def clone(self):
        """Clone the underlying :class:`.Registry`."""
        self.store["registry"].clone()

    def add_to_registry(self, urn: str):
        """Copy data for `urn` from :class:`.LocalStore` to the :class:`.Registry`."""
        obj = self.store["local"].get(urn)
        self.store["registry"].write(obj)


# Command-line interface


@click.group("store")
@click.pass_context
def main(context) -> None:
    """Manipulate local data storage."""


@main.command()
@click.pass_obj
def clone(context):
    """Clone the registry.

    The registry is cloned into the directory specified by the `tdc_registry_local`
    config value. See `tdc config --help`.
    """
    from transport_data import STORE

    STORE.clone()


@main.command("list")
@click.argument("maintainer_id", metavar="MAINTAINER")
@click.pass_context
def list_cmd(context, maintainer_id):
    """List store contents for MAINTAINER."""
    from transport_data import STORE

    for urn in STORE.list(maintainer_id):
        print(urn)


@main.command()
@click.argument("partial_urn", metavar="URN")
@click.pass_context
def show(context, partial_urn):
    """Display an SDMX object by URN.

    The URN should be partial, starting with the object class, for instance
    "Codelist=AGENCY:ID(1.2.3)".
    """
    from transport_data import STORE

    obj = STORE.get(partial_urn)

    print(repr(obj))

    if isinstance(obj, m.ItemScheme):
        # Display members of the ItemScheme
        for i, (_, item) in enumerate(obj.items.items()):
            print(f"{i:>3} {repr(item)}")
