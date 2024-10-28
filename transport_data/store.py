"""Local data storage.

.. todo:: Add the following to base capabilities of :class:`.UnionStore`::

   - :py:`write(..., annotate=True)`
"""

import logging
from typing import TYPE_CHECKING

import click
import dsss.store
import sdmx.model.v21 as m
import sdmx.urn

from transport_data.util.sdmx import anno_generated

if TYPE_CHECKING:
    import transport_data.config

log = logging.getLogger(__name__)


class UnionStore(dsss.store.UnionStore):
    """A store that maps between a :class:`.LocalStore` and :class:`.Registry`.

    This class extends :class:`dsss.store.UnionStore` with the following behaviour:

    - The sub-stores are initialized from an instance of :class:`.Config`.
    - :meth:`assign_version` and :meth:`get` have extended behaviour. See the
      documentation of each method.
    - Additional methods :meth:`clone` and :meth:`add_to_registry`.
    """

    def __init__(self, config: "transport_data.config.Config") -> None:
        super().__init__(
            hook={"before set": anno_generated},
            store=dict(
                local=dsss.store.FlatFileStore(path=config.data_path.joinpath("local")),
                registry=dsss.store.GitStore(
                    path=config.data_path.joinpath("registry"),
                    remote_url=config.registry_remote_url,
                ),
            ),
        )
        # FIXME Include in the above call, once dsss.store.UnionStore supports
        self.maintainer_store.update(ISO="registry")

    # Overrides of methods of dsss.store.UnionStore or its parents

    def assign_version(self, obj, **kwargs) -> None:
        """Assign a version to `obj` subsequent to any existing versions.

        Compared to the parent class, this implementation ensures that the assigned
        version is :class:`str`. This is needed because :mod:`sdmx` currently fails to
        write :class:`.Version` to SDMX-ML.

        .. todo:: Remove this override once the issue is fixed in :mod:`sdmx`.
        """
        super().assign_version(obj, **kwargs)
        obj.version = str(obj.version)

    def get(self, key: str):
        """Return an object given its `key`.

        Compared to the parent class, this implementation:

        - Expands `key` from a partial URN (e.g. "AgencyScheme=TDCI:TDCI(1.0.0)") to a
          full URN.
        - Handles `key` that is a partial URN without a specific version, e.g.
          "AgencyScheme=TDCI:TDCI". In this case, the greatest version of the referenced
          artefact is returned.
        """
        try:
            full_urn = sdmx.urn.expand(key)
            return super().get(full_urn)
        except KeyError:
            match = sdmx.urn.match(full_urn)
            if match and match["version"] is None:
                if versions := self.list_versions(
                    m.get_class(match["class"]), match["agency"], match["id"]
                ):
                    return super().get(full_urn.replace("(None)", f"({versions[-1]})"))
            raise

    # Additional methods for this class

    def add_to_registry(self, urn: str):
        """Copy data for `urn` from :class:`.LocalStore` to the :class:`.Registry`."""
        full_urn = sdmx.urn.expand(urn)
        obj = self.store["local"].get(full_urn)
        self.store["registry"].set(obj)

    # FIXME Restore this original once the upstream issue is resolved
    # def clone(self):
    #     """Clone the underlying :class:`.Registry`."""
    #     self.store["registry"].clone()

    def clone(self):
        """Clone the underlying :class:`.Registry`.

        Temporary version to work around `khaeru/dsss#19
        <https://github.com/khaeru/dsss/issues/19>`_. This is identical to
        :meth:`dsss.store.GitStore.clone`, except only certain paths are checked out.
        """
        import git

        s = self.store["registry"]

        # Ensure there is a remote for the origin
        try:
            s.repo.delete_remote("origin")
        except git.exc.GitCommandError:
            pass

        origin = s.repo.create_remote("origin", s.remote_url)

        # Fetch the remote
        branch_name = "main"
        origin.fetch(f"refs/heads/{branch_name}")
        b = origin.refs[branch_name]

        # Check out the branch
        try:
            head = s.repo.heads[branch_name]
        except IndexError:
            head = s.repo.create_head(branch_name, b)

        head.set_tracking_branch(b)
        # Omits ISO
        s.repo.git.checkout("main", "--", "ADB", "ESTAT", "IAMC", "TDCI")


# Command-line interface


@click.group("store")
@click.pass_context
def main(context) -> None:
    """Manipulate local SDMX (meta)data."""


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
@click.option("--maintainer", "maintainer_id")
@click.pass_context
def list_cmd(context, maintainer_id):
    """List contents of the store."""
    from transport_data import STORE

    for urn in sorted(STORE.list(maintainer=maintainer_id)):
        print(sdmx.urn.shorten(urn))


@main.command()
@click.argument("partial_urn", metavar="URN")
@click.pass_context
def show(context, partial_urn):
    """Display an SDMX object by URN.

    The URN should be partial, starting with the object class, for instance
    "Codelist=AGENCY:ID(1.2.3)".

    .. todo:: Use :class:`.Report` instances where possible.
    """
    from transport_data import STORE

    obj = STORE.get(partial_urn)

    print(repr(obj))

    if isinstance(obj, m.ItemScheme):
        # Display members of the ItemScheme
        for i, (_, item) in enumerate(obj.items.items()):
            print(f"{i:>3} {repr(item)}")
