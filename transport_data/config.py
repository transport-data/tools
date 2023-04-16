import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Optional

import click
from xdg_base_dirs import xdg_config_home


@dataclass
class Config:
    """Common configuration."""

    #: Path to the configuration file read, if any
    config_path: Optional[Path] = None

    #: Path to a local clone of https://github.com/transport-data/registry.
    tdc_registry_local: Path = field(default_factory=Path.cwd)

    def __post_init__(self):
        self.tdc_registry_local = Path(self.tdc_registry_local)

    @classmethod
    def read(cls):
        # Candidate path for the configuration file
        config_path = xdg_config_home().joinpath("transport-data", "config.json")

        if config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
            data.update(config_path=config_path)
        else:
            # No file exists → defaults for all settings
            data = dict()

        return cls(**data)

    def write(self):
        config_dir = xdg_config_home().joinpath("transport-data")
        if not config_dir.exists():
            print(f"Create {config_dir}")
            config_dir.mkdir(parents=True, exist_ok=True)

        path = config_dir.joinpath("config.json")

        # Convert dataclass instance to dict; omit the path to the file itself
        data = asdict(self)
        data.pop("config_path")

        # Write to config.json
        path.write_text(json.dumps(data, indent=2))
        print(f"Wrote {path}")


@click.group("config")
def main():
    """Manipulate configuration."""
    pass


@main.command("set")
@click.argument("key")
@click.argument("value")
def set_cmd(key, value):
    """Set config KEY to VALUE."""
    from transport_data import CONFIG

    # Validate `key`
    field_names = [f.name for f in fields(CONFIG)]
    if key not in field_names:
        raise click.ClickException(
            f"{key!r} not among configuration keys {field_names}"
        )

    # Set the value
    setattr(CONFIG, key, value)

    # Write the configuration file
    CONFIG.write()


@main.command()
def show():
    """Display config values."""
    from transport_data import CONFIG

    print(*[f"{k}: {v}" for k, v in asdict(CONFIG).items()], sep="\n")
