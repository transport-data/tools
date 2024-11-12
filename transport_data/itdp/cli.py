"""CLI for :mod:`.itdp`.

.. runblock:: console

   $ tdc itdp --help

.. runblock:: console

   $ tdc itdp fetch --help
"""

import click


@click.group("itdp")
def main():
    """Institute for Transport and Development Policy (ITDP).

    Fetch and convert data from the Rapid Transit Database.
    """
    from .rtdb import convert, fetch

    result = convert(fetch())
    print(result)
