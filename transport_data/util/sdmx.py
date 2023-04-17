from datetime import datetime
from importlib.metadata import version

import sdmx.model.v21 as m


def anno_generated(obj: m.AnnotableArtefact):
    """Annotate the `obj` with information about how it was generated."""
    obj.annotations.append(
        m.Annotation(
            id="tdc-generated",
            text=f"{datetime.now().isoformat()} "
            f"by transport_data v{version('transport_data')}",
        )
    )
