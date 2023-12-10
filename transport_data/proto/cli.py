"""CLI for :mod:`.proto`.

.. runblock:: console

   $ tdc proto --help

"""
import click


@click.command("proto")
def main():  # pragma: no cover
    """TDC prototype debugging."""
    # from transport_data import adb
    from transport_data import jrc

    # # commented: this fetches *all* data, and should not be done too often
    # # jrc.extract_all()
    #
    # # commented: uncomment these statements to fetch and unpack just one data file
    # path = jrc.fetch("AT")
    # jrc.extract(path)

    print(jrc.read("AT"))

    # # commented: uncomment this statement to fetch ADB ATO data files
    # adb.get()

    # adb.convert_all()
