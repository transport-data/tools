from transport_data import hook


@hook
def cli_modules() -> str:
    return f"{__name__}.cli"
