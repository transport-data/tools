"""Sustainable Urban Mobility for All (SUM4All) data provider."""

from transport_data.util.pluggy import hookimpl


@hookimpl
def get_agencies():
    """Return the ``ISO`` :class:`~.sdmx.model.common.Agency`."""
    from sdmx.model import common

    a = common.Agency(
        id="SUM4ALL",
        name="Sustainable Urban Mobility for All",
        contact=[common.Contact(uri=["https://sum4all.org"])],
    )
    return (a,)
