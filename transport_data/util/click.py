"""Utilities for :mod:`click`."""

import click

PARAM = {"version": click.Option(["--version"])}


def common_params(names: str) -> list:
    """Return parameters from `PARAM`."""
    return list(PARAM[k] for k in names.split())
