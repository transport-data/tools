"""Manipulate the registry repo."""
import subprocess

import click


def _gh(*parts):
    """Invoke `gh`, the GitHub CLI client."""
    return subprocess.run(("gh",) + parts)


def _git(*parts):
    """Invoke `git` in the :attr:`Config.tdc_registry_local` directory."""
    from transport_data import CONFIG

    return subprocess.run(("git", "-C", str(CONFIG.tdc_registry_local)) + parts)


@click.group("registry", help=__doc__)
def main():
    pass


@main.command()
def clone():
    """Clone the registry.

    The registry is cloned into the directory specified by the `tdc_registry_local`
    config value. See `tdc config --help`.
    """
    from transport_data import CONFIG

    _gh("repo", "clone", "transport-data/registry", str(CONFIG.tdc_registry_local))


@main.command(hidden=True)
def status():
    """Example command using `git`."""
    _git("status")
