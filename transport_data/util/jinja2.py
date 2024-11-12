"""Utilities for :mod:`jinja2`."""

from functools import lru_cache


@lru_cache
def get_env():
    """Return a Jinja2 environment for rendering templates."""
    from jinja2 import Environment, PackageLoader, select_autoescape

    from transport_data import util
    from transport_data.org import metadata

    # Create a Jinja environment
    env = Environment(
        loader=PackageLoader("transport_data", package_path="data/template"),
        extensions=["jinja2.ext.loopcontrols"],
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Update filters
    def _get_reported_attribute(mdr, id_):
        for ra in mdr.metadata:
            if ra.value_for.id == id_:
                return ra.value, ra.value_for
        return "—", None

    def _format_desc(dim):
        try:
            anno_description = dim.get_annotation(id="tdc-description")
            if desc := str(anno_description.text):
                return desc
            else:
                raise KeyError
        except KeyError:
            return "—"

    env.filters["dfd_id"] = metadata.dfd_id
    env.filters["domain"] = util.url_hostname
    env.filters["format_desc"] = _format_desc
    env.filters["rst_heading"] = util.uline

    return env, dict(
        get_reported_attribute=_get_reported_attribute,
    )
