import click

from . import GEO, POOCH, convert


@click.group("jrc", help=__doc__)
def main():
    pass


@main.command
@click.argument("geo", nargs=-1)
@click.option("--go", is_flag=True, help="Actually fetch.")
@click.option("--all", "all_", is_flag=True, help="Fetch all files.")
def fetch(geo, all_, go):
    if not len(geo):
        if not all_:
            print(f"Supply --all or 1+ of {GEO}")
            return

        geo = GEO

    if not go:
        for g in geo:
            print(f"Valid url for GEO={g}: {POOCH.is_available(g)}")
        return

    for g in geo:
        POOCH.fetch(g)


@main.command("convert")
@click.argument("geo", nargs=-1)
def convert_cmd(geo):
    for g in geo:
        convert(g)
