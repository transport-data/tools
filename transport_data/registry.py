"""Manipulate the registry repo."""
import subprocess

import click
import sdmx
import sdmx.model.v21 as m

from transport_data import CONFIG


def _gh(*parts):
    """Invoke `gh`, the GitHub CLI client."""
    return subprocess.run(("gh",) + parts)


def _git(*parts):
    """Invoke `git` in the :attr:`Config.tdc_registry_local` directory."""
    return subprocess.run(("git", "-C", str(CONFIG.tdc_registry_local)) + parts)


def path_for(obj: m.MaintainableArtefact):
    """Determine a path and filename for `obj`."""
    if obj.urn is None:
        obj.urn = sdmx.urn.make(obj)

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

    with open(path, "wb") as f:
        f.write(sdmx.to_xml(obj, pretty_print=True))

    print(f"Wrote {path}")

    # Add to git, but do not commit
    _git("add", str(path.relative_to(CONFIG.tdc_registry_local)))
    _git("status")


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
