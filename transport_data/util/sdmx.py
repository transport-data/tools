"""Utilities for :mod:`sdmx`."""
from datetime import datetime
from importlib.metadata import version

import sdmx.model.v21 as m


def anno_generated(obj: m.AnnotableArtefact):
    """Annotate the `obj` with information about how it was generated."""
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
