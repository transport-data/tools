"""Manipulate the registry repo."""
import logging
import re
import subprocess
from functools import singledispatchmethod
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple, Union

import click
import packaging.version
import sdmx
import sdmx.model.v21 as m
import sdmx.urn
from sdmx.message import StructureMessage
from sdmx.reader.xml import Reader

from transport_data.util.sdmx import anno_generated

if TYPE_CHECKING:
    import transport_data.config

log = logging.getLogger(__name__)


def _full_urn(value: str) -> str:
    """Convert possibly partial `value` to a complete SDMX URN."""
    urn_base = "urn:sdmx:org.sdmx.infomodel.class."
    if value.startswith(urn_base):
        return value
    else:
        return f"{urn_base}{value}"


class Store:
    """A class for storage of SDMX artefacts."""

    path: Path

    def __init__(self, config: "transport_data.config.Config") -> None:
        self.path = config.tdc_registry_local

    def _gh(self, *parts):
        """Invoke `gh`, the GitHub CLI client."""
        return subprocess.run(("gh",) + parts)

    def _git(self, *parts):
        """Invoke `git` in the :attr:`path` directory."""
        return subprocess.run(("git", "-C", str(self.path)) + parts)

    def clone(self):
        self._gh("repo", "clone", "transport-data/registry", str(self.path))

    @singledispatchmethod
    def path_for(self, obj: m.MaintainableArtefact) -> Path:
        """Determine a path and filename for `obj`."""
        version = obj.version or "0"
        return self.path.joinpath(
            obj.maintainer.id,
            f"{obj.__class__.__name__}_{obj.maintainer.id}_{obj.id}_"
            f"{version.replace('.', '-')}",
        ).with_suffix(".xml")

    @path_for.register
    def _(self, obj: m.DataSet) -> Path:
        """Determine a path and filename for `obj`."""
        # Generate a path for the data set's corresponding data flow
        tmp = self.path_for(obj.described_by)
        return tmp.with_name(tmp.name.replace("DataflowDefinition", "DataSet"))

    @path_for.register
    def _(self, urn: str) -> Path:
        m = sdmx.urn.match(_full_urn(urn))
        return self.path.joinpath(
            m["agency"],
            "_".join(
                [m["class"], m["agency"], m["id"], m["version"].replace(".", "-")]
            ),
        ).with_suffix(".xml")

    @singledispatchmethod
    def write(
        self,
        obj: Union[m.MaintainableArtefact, m.DataSet],
        *,
        annotate: bool = True,
        force: bool = False,
        _show_status: bool = False,
    ) -> Path:
        """Write `obj` into the registry as SDMX-ML.

        The path and filename are determined by the object properties.
        """
        path = self.path_for(obj)

        if path.exists() and not force:
            raise RuntimeError(f"Will not overwrite {path} without force=True")

        # Make the parent directory (but not multiple parents)
        path.parent.mkdir(exist_ok=True)

        if isinstance(obj, m.AnnotableArtefact) and annotate:
            # Annotate the object with information about how it was generated
            # TODO don't do this for files retrieved directly from an SDMX API
            anno_generated(obj)

        with open(path, "wb") as f:
            f.write(sdmx.to_xml(obj, pretty_print=True))

        print(f"Wrote {path}")

        if isinstance(obj, m.DataSet):
            csv_path = path.with_suffix(".csv")
            sdmx.to_csv(obj, path=csv_path, attributes="gso")
            print(f"Wrote {csv_path}")

        # Add to git, but do not commit
        # NB if the path is specifically covered by a .gitignore entry, this will generate
        #    some advice messages but have no effect. See e.g. registry/ESTAT/README.
        # TODO ignore "The following paths are ignored by one of your .gitignore files"
        self._git("add", str(path.relative_to(self.path)))
        if _show_status:
            self._git("status")

        return path

    @write.register
    def _(self, obj: StructureMessage, **kwargs):
        # Write each of the structure objects a separate file
        for kind in ("codelist", "concept_scheme", "dataflow", "structure"):
            for obj_ in getattr(obj, kind).values():
                self.write(obj_, **kwargs, _show_status=False)

        self._git("status")

    def list_versions(self, obj: m.MaintainableArtefact) -> List[str]:
        """List all versions of `obj` already stored in the registry."""
        # Path that would result from writing `obj`
        path = self.path_for(obj)

        # Expression matching similar file names with different versions
        expr = re.compile("(.*_)(?P<version>[0-9-]+)(.xml)")

        # A glob pattern for similar names
        pattern = expr.sub(r"\1*\3", str(path.name))

        # Extract just the version part of the names of matching files; restore "."
        versions = sorted(
            map(
                lambda p: expr.fullmatch(p.name).group("version").replace("-", "."),  # type: ignore [union-attr]
                path.parent.glob(pattern),
            )
        )

        return versions

    def next_version(
        self, obj: m.MaintainableArtefact, major=False, minor=True, patch=False
    ) -> str:
        """Return an incremented version string for `obj`."""
        v = packaging.version.parse(self.list_versions(obj)[-1])
        return f"{v.major + int(major)}.{v.minor + int(minor)}.{v.micro + int(patch)}"

    def assign_version(
        self,
        obj: m.MaintainableArtefact,
        default="0.0.0",
        increment: Union[bool, Tuple[bool, bool, bool]] = False,
    ):
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


# Command-line interface


@click.group("registry", help=__doc__)
@click.pass_context
def main(context):
    context.default_store = Store()


@main.command()
@click.pass_context
def clone(context):
    """Clone the registry.

    The registry is cloned into the directory specified by the `tdc_registry_local`
    config value. See `tdc config --help`.
    """
    context.default_store.clone()


@main.command("list")
@click.argument("maintainer_id", metavar="MAINTAINER")
@click.pass_context
def list_cmd(context, maintainer_id):
    """List registry contents for MAINTAINER."""
    base = context.default_store.path.joinpath(maintainer_id)
    for f in sorted(base.glob("*.xml")):
        print(f.relative_to(base))


@main.command()
@click.argument("partial_urn", metavar="URN")
@click.pass_context
def show(context, partial_urn):
    """Display an SDMX object by URN.

    The URN should be partial, starting with the object class, e.g.
    Codelist=AGENCY:ID(1.2.3).
    """
    # Path to the object
    urn = _full_urn(partial_urn)
    candidate = context.default_store.path_for(urn)
    if not candidate.exists():
        raise click.ClickException(f"No path {candidate}")

    r = Reader()
    try:
        obj = r.read_message(candidate)
    except RuntimeError as e:
        if "uncollected items" in str(e):
            print(candidate.read_text())
            return

    if obj is None:
        m = sdmx.urn.match(urn)
        klass = sdmx.model.get_class(m["class"])
        obj = r.get_single(klass)

    print(repr(obj))

    if isinstance(obj, m.ItemScheme):
        # Display members of the ItemScheme
        for i, (_, item) in enumerate(obj.items.items()):
            print(f"{i:>3} {repr(item)}")
