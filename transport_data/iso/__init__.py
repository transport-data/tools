"""International Organization for Standardization (ISO)."""

import logging

from sdmx.model import common

from transport_data.util.pluggy import hookimpl

log = logging.getLogger(__name__)


@hookimpl
def get_agencies():
    """Return the ``ISO`` :class:`~.sdmx.model.common.Agency`."""
    a = common.Agency(
        id="ISO",
        name="International Organization for Standardization",
        contact=[common.Contact(uri=["https://iso.org"])],
    )
    return (a,)
