import click

from transport_data import registry


@click.command("org")
def main():
    """Information about the TDCI per se."""
    from . import gen_structures

    registry.write(gen_structures())
