"""Utilities."""

from itertools import chain
from urllib.parse import urlparse


def list_urns() -> list[str]:
    """List all URNs of SDMX artefacts provided by :mod:`tranport_data` and plugins."""
    from transport_data.util.pluggy import pm

    return list(chain(*pm.hook.provides()))


def uline(text: str, char: str = "=") -> str:
    """Underline `text` with `char`."""
    return f"{text}\n{char * len(text)}"


def url_hostname(value: str) -> str:
    """If `value` contains a URL, return its hostname."""
    try:
        return urlparse(value).hostname or ""
    except Exception:
        return value
