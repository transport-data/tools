from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Common configuration."""

    #: Path to a local clone of https://github.com/transport-data/registry.
    tdc_registry_local: Path
