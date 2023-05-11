import click

from . import POOCH


@click.group("jrc", help=__doc__)
def main():
    pass


@main.command("fetch")
@click.argument("geo")
@click.option("--go", is_flag=True)
def fetch(geo, go):
    print(POOCH.is_available(geo))

    if not go:
        return

    print(POOCH.fetch(geo))
