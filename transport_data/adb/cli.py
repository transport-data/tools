import click

from . import FILES, convert, fetch


@click.group("adb", help=__doc__)
def main():
    """Asian Development Bank (ADB) provider."""


@main.command("fetch")
@click.argument("part", nargs=-1)
@click.option("--go", is_flag=True, help="Actually fetch.")
@click.option("--all", "all_", is_flag=True, help="Fetch all files.")
def fetch_cmd(part, all_, go):
    if not len(part):
        if not all_:
            print(f"Supply --all or 1+ of {FILES.keys()}")
            return

        part = list(FILES.keys())

    fetch(*part)


@main.command("convert")
@click.argument("part", nargs=-1)
def convert_cmd(part):
    for p in part:
        convert(p)
