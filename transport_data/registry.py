"""Manipulate the registry repo."""
import re
import subprocess
from functools import singledispatch
from pathlib import Path
from typing import Tuple, Union

import click
import packaging.version
import sdmx
import sdmx.model.v21 as m
from sdmx import urn
from sdmx.message import StructureMessage
from sdmx.reader.xml import Reader

from transport_data import CONFIG
from transport_data.util.sdmx import anno_generated


def _gh(*parts):
    """Invoke `gh`, the GitHub CLI client."""
    return subprocess.run(("gh",) + parts)


def _git(*parts):
    """Invoke `git` in the :attr:`Config.tdc_registry_local` directory."""
    return subprocess.run(("git", "-C", str(CONFIG.tdc_registry_local)) + parts)


@singledispatch
def path_for(obj: m.MaintainableArtefact) -> Path:
    """Determine a path and filename for `obj`."""
    version = obj.version or "0"
    return CONFIG.tdc_registry_local.joinpath(
        obj.maintainer.id,
        f"{obj.__class__.__name__}_{obj.maintainer.id}_{obj.id}_"
        f"{version.replace('.', '-')}",
    ).with_suffix(".xml")


@path_for.register
def _(obj: m.DataSet) -> Path:
    """Determine a path and filename for `obj`."""
    # Generate a path for the data set's corresponding data flow
    tmp = path_for(obj.described_by)
    return tmp.with_name(tmp.name.replace("DataflowDefinition", "DataSet"))


@singledispatch
def write(
    obj: Union[m.MaintainableArtefact, m.DataSet],
    *,
    annotate=True,
    force=False,
    _show_status=True,
):
    """Write `obj` into the registry as SDMX-ML.

    The path and filename are determined by the object properties.
    """
    path = path_for(obj)

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
    _git("add", str(path.relative_to(CONFIG.tdc_registry_local)))
    if _show_status:
        _git("status")

    return path


@write.register
def _(obj: StructureMessage, **kwargs):
    # Write each of the structure objects a separate file
    for kind in ("codelist", "concept_scheme", "dataflow", "structure"):
        for obj_ in getattr(obj, kind).values():
            write(obj_, **kwargs, _show_status=False)

    _git("status")


def list_versions(obj: m.MaintainableArtefact) -> list[str]:
    """List all versions of `obj` already stored in the registry."""
    # Path that would result from writing `obj`
    path = path_for(obj)

    # Expression matching similar file names with different versions
    expr = re.compile("(.*_)(?P<version>[0-9-]+)(.xml)")

    # A glob pattern for similar names
    pattern = expr.sub(r"\1*\3", str(path.name))

    # Extract just the version part of the names of matching files; restore "."
    versions = sorted(
        map(
            lambda p: expr.fullmatch(p.name).group("version").replace("-", "."),
            path.parent.glob(pattern),
        )
    )

    return versions


def next_version(
    obj: m.MaintainableArtefact, major=False, minor=True, patch=False
) -> str:
    """Return an incremented version string for `obj`."""
    v = packaging.version.parse(list_versions(obj)[-1])
    return f"{v.major + int(major)}.{v.minor + int(minor)}.{v.micro + int(patch)}"


def assign_version(
    obj: m.MaintainableArtefact,
    default="0.0.0",
    increment: Union[bool, Tuple[bool, bool, bool]] = False,
):
    """Assign a version to `obj`.

    If `increment` is :data:`False`, the version will be the latest already existing in
    the registry, if any, or `default` if no version of `obj` is stored.

    Otherwise, `increment` should be a 3-tuple of :class:`bool`, which are passed as
    arguments to :func:`next_version`.
    """
    if increment is False:
        obj.version = (list_versions(obj) or [default])[-1]
    else:
        if not isinstance(increment, tuple):
            increment = (increment, False, False)
        obj.version = next_version(obj, *increment)


# Command-line interface


@click.group("registry", help=__doc__)
def main():
    pass


@main.command()
def clone():
    """Clone the registry.

    The registry is cloned into the directory specified by the `tdc_registry_local`
    config value. See `tdc config --help`.
    """
    _gh("repo", "clone", "transport-data/registry", str(CONFIG.tdc_registry_local))


@main.command("list")
@click.argument("maintainer_id", metavar="MAINTAINER")
def list_cmd(maintainer_id):
    """List registry contents for MAINTAINER."""
    base = CONFIG.tdc_registry_local.joinpath(maintainer_id)
    for f in sorted(base.glob("*.xml")):
        print(f.relative_to(base))


@main.command()
@click.argument("partial_urn", metavar="URN")
def show(partial_urn):
    """Display an SDMX object by URN.

    The URN should be partial, starting with the object class, e.g.
    Codelist=AGENCY:ID(1.2.3).
    """
    # TODO handle missing version
    result = urn.match(f"urn:sdmx:org.sdmx.infomodel.class.{partial_urn}")

    candidate = CONFIG.tdc_registry_local.joinpath(
        result["agency"],
        "_".join(
            [
                result["class"],
                result["agency"],
                result["id"],
                result["version"].replace(".", "-"),
            ]
        ),
    ).with_suffix(".xml")

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
        klass = sdmx.model.get_class(result["class"])
        obj = r.get_single(klass)

    print(repr(obj))

    if isinstance(obj, m.ItemScheme):
        for i, (_, item) in enumerate(obj.items.items()):
            print(f"{i:>3} {repr(item)}")
