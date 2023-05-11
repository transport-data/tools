import click

from . import GEO, convert, fetch


@click.group("jrc", help=__doc__)
def main():
    """EU Joint Research Center (JRC) provider."""


@main.command
@click.argument("geo", nargs=-1)
@click.option("--go", is_flag=True, help="Actually fetch.")
@click.option("--all", "all_", is_flag=True, help="Fetch all files.")
def fetch_cmd(geo, all_, go):
    if not len(geo):
        if not all_:
            print(f"Supply --all or 1+ of {GEO}")
            return

        geo = GEO

    fetch(*geo, dry_run=not go)


@main.command("convert")
@click.argument("geo", nargs=-1)
def convert_cmd(geo):
    for g in geo:
        convert(g)
