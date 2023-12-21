import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Optional

import click
from platformdirs import user_config_path, user_data_path


@dataclass
class Config:
    """Common configuration."""

    #: Path to the configuration file read, if any
    config_path: Optional[Path] = None

    #: Path to a local clone of https://github.com/transport-data/registry.
    data_path: Path = field(
        default_factory=lambda: user_data_path("transport-data", ensure_exists=True)
    )

    #: Mapping from maintainer IDs to either "local" (stored in a :class:`.LocalStore`)
    #: or "registry" (stored in the :class:`.Registry`).
    store_map: dict = field(
        default_factory=lambda: {"TDCI": "registry", "TEST": "local"}
    )

    @staticmethod
    def _config_path():
        """Candidate path for the configuration file."""
        return user_config_path("transport-data").joinpath("config.json")

    @classmethod
    def read(cls):
        cp = cls._config_path()
        if cp.exists():
            with open(cp) as f:
                data = json.load(f)
            data.update(config_path=cp)
        else:
            # No file exists → defaults for all settings
            data = dict()

        return cls(**data)

    def write(self):
        cp = self._config_path()
        if not cp.parent.exists():
            print(f"Create {cp.parent}")
            cp.parent.mkdir(parents=True, exist_ok=True)

        # Convert dataclass instance to dict; omit the path to the file itself
        data = asdict(self)
        data.pop("config_path")
        data["tdc_registry_local"] = str(data["tdc_registry_local"])

        # Write to config.json
        cp.write_text(json.dumps(data, indent=2))
        print(f"Wrote {cp}")


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
