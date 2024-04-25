"""Utilities for :mod:`sdmx`."""

from datetime import datetime
from importlib.metadata import version
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    import sdmx.model.v21


def anno_generated(obj: "sdmx.model.common.AnnotableArtefact") -> None:
    """Annotate the `obj` with information about how it was generated."""
    from sdmx.model import v21 as m

    try:
        # Retrieve existing annotation
        anno = obj.get_annotation(id="tdc-generated")
    except KeyError:
        # Create a new annotation
        anno = m.Annotation(id="tdc-generated")
        obj.annotations.append(anno)

    anno.text = (
        f"{datetime.now().isoformat()} by transport_data v{version('transport_data')}"
    )


def make_obs(
    row: "pd.Series", dsd: "sdmx.model.v21.DataStructureDefinition"
) -> "sdmx.model.v21.Observation":
    """Helper function for making :class:`sdmx.model.Observation` objects."""
    from sdmx.model import v21 as m

    key = dsd.make_key(m.Key, row[[d.id for d in dsd.dimensions]].to_dict())

    # Attributes
    attrs = {}
    for a in filter(
        lambda a: isinstance(a.related_to, m.PrimaryMeasureRelationship), dsd.attributes
    ):
        # Only store an AttributeValue if there is some text
        value = row[a.id]
        if not pd.isna(value):
            attrs[a.id] = m.AttributeValue(value_for=a, value=value)

    pm = dsd.measures[0]
    return m.Observation(
        dimension=key, attached_attribute=attrs, value_for=pm, value=row[pm.id]
    )
