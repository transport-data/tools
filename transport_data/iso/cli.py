"""CLI for :mod:`.iso`.

.. runblock:: console

   $ tdc iso --help

"""

import click


@click.group(name="iso")
def main():
    """International Organization for Standardization (ISO) provider."""


@main.command
def refresh():  # pragma: no cover
    """Regenerate the ISO code lists."""
    from transport_data.iso import generate_all

    generate_all()
