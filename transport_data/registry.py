"""Manipulate the registry repo."""
import re
import subprocess
from typing import Tuple, Union

import click
import packaging.version
import sdmx
import sdmx.model.v21 as m

from transport_data import CONFIG
from transport_data.util.sdmx import anno_generated


def _gh(*parts):
    """Invoke `gh`, the GitHub CLI client."""
    return subprocess.run(("gh",) + parts)


def _git(*parts):
    """Invoke `git` in the :attr:`Config.tdc_registry_local` directory."""
    return subprocess.run(("git", "-C", str(CONFIG.tdc_registry_local)) + parts)


def path_for(obj: m.MaintainableArtefact):
    """Determine a path and filename for `obj`."""
    version = obj.version or "0"
    return CONFIG.tdc_registry_local.joinpath(
        obj.maintainer.id,
        f"{obj.__class__.__name__}_{obj.maintainer.id}_{obj.id}_"
        f"{version.replace('.', '-')}",
    ).with_suffix(".xml")


def write(obj: m.MaintainableArtefact, force=False):
    """Write `obj` into the registry as SDMX-ML.

    The path and filename are determined by the object properties.
    """
    path = path_for(obj)

    if path.exists() and not force:
        raise RuntimeError(f"Will not overwrite {path} without force=True")

    # Make the parent directory (but not multiple parents)
    path.parent.mkdir(exist_ok=True)

    # Annotate the object with information about how it was generated
    anno_generated(obj)

    with open(path, "wb") as f:
        f.write(sdmx.to_xml(obj, pretty_print=True))

    print(f"Wrote {path}")

    # Add to git, but do not commit
    _git("add", str(path.relative_to(CONFIG.tdc_registry_local)))
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
