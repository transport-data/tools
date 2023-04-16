import click


@click.command("org")
def main():
    import sdmx

    from . import gen_structures

    print(sdmx.to_xml(gen_structures(), pretty_print=True).decode())
