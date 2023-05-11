import click

from . import POOCH, convert_all


@click.group("adb", help=__doc__)
def main():
    pass


@main.command("fetch")
@click.argument("part")
@click.option("--go", is_flag=True)
def fetch(part, go):
    print(POOCH.is_available(part))

    if not go:
        return

    print(POOCH.fetch(part))


@main.command("convert")
def convert_cmd():
    """Convert data to SDMX."""
    convert_all()
