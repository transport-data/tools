import click

from transport_data import registry


@click.command("org")
def main():
    """Information about the TDCI per se."""
    from . import get_agencyscheme

    registry.write(get_agencyscheme(), force=True)
