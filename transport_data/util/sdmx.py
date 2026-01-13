"""Utilities for :mod:`sdmx`."""

import io
from dataclasses import fields
from datetime import datetime
from importlib.metadata import version
from inspect import getsource
from io import StringIO
from textwrap import dedent
from token import COMMENT, NAME
from tokenize import generate_tokens
from typing import TYPE_CHECKING, cast

import pandas as pd

if TYPE_CHECKING:
    import pathlib
    from typing import TypedDict

    import sdmx.model.common
    import sdmx.model.v21
    import sdmx.model.v30

    # Types for dicts holding keyword arguments to SDMX classes
    # TODO Move upstream
    class IAKeywords(TypedDict, total=False):
        id: str

    class VAKeywords(IAKeywords):
        version: str

    class MAKeywords(VAKeywords):
        maintainer: sdmx.model.common.Agency | None


class CSVAdapter(io.RawIOBase):
    """Adapt CSV content from `path` into SDMX-CSV.

    The `SDMX-CSV <https://github.com/sdmx-twg/sdmx-csv/blob/master/data-message/docs/sdmx-csv-field-guide.md>`_
    format has precise requirements for identifier and other columns. In particular, the
    "STRUCTURE", "STRUCTURE_ID", and "ACTION" columns are mandatory.

    .. code-block::

       STRUCTURE,STRUCTURE_ID,ACTION,DIM_1,DIM_2,DIM_3,OBS_VALUE
       dataflow,ESTAT:NA_MAIN(1.6.0),I,A,B,2014-01,12.4

    This class produces standard SDMX-CSV by adapting a simplified format such as:

    .. code-block::

       DIM_1,DIM_2,DIM_3,OBS_VALUE
       A,B,2014-01,12.4

    In particular:

    - The header line of `path` is prefixed with "STRUCTURE", "STRUCTURE_ID", and/or
      "ACTION" if the respective parameters are given.
    - Every record (line) of `path` is prefixed with the *values* of the respective
      parameters.

    So, for instance, to transform the above example into the first example, use a
    CSVAdapter with:

    .. code-block:: python

       a = CSVAdapter(
           path,
           structure="dataflow",
           structure_id="ESTAT:NA_MAIN(1.6.0)",
           action="I",
       )
       data = a.read()

    Parameters
    ----------
    structure :
        Value for the "STRUCTURE" SDMX-CSV field, to be inserted into every record.
    structure_id :
        Value for the "STRUCTURE_ID" field, to be inserted into every record.
    action :
        Value for the "ACTION" field, to be inserted into every record.
    """

    def __init__(
        self,
        path: "pathlib.Path",
        structure: str | None = None,
        structure_id: str | None = None,
        action: str | None = None,
    ) -> None:
        self._path = path

        # Determine fields to prefix to header line and records
        header, line = [], []
        for column, value in (
            (b"STRUCTURE", structure),
            (b"STRUCTURE_ID", structure_id),
            (b"ACTION", action),
        ):
            if value is not None:
                header.append(column)
                line.append(value.encode())

        # Construct single `bytes`` for header and line prefixes
        self._header_prefix = b",".join((header + [b""]) if len(header) else [])
        self._line_prefix = b",".join((line + [b""]) if len(line) else [])

    def readall(self, size: int = -1, /) -> bytes:
        """Read and adapt CSV to SDMX-CSV.

        .. todo:: This currently reads and adapts the entire file at once; this may not
           be performant for very large files. Improve to handle lines individually or
           in batches.
        """
        lines = []
        with open(self._path, "rb") as f:
            lines = [
                (self._header_prefix if i == 0 else self._line_prefix) + line
                for i, line in enumerate(f)
            ]

        return b"".join(lines)


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


def read_csv(
    path: "pathlib.Path",
    structure: "sdmx.model.v30.Dataflow | sdmx.model.v30.DataStructureDefinition",
    adapt: dict | None = None,
) -> "sdmx.message.DataMessage":
    """Read or adapt SDMX-CSV from `path`.

    Parameters
    ----------
    path :
        A file in SDMX-CSV or CSV format.
    structure :
        Data flow or data structure describing the contents of `path`.
    adapt :
        Keyword arguments to :class:`CSVAdapter`. If given, the contents of `path` are
        adapted from a ‘simplified’ or ‘reduced’ CSV format to SDMX-CSV on-the-fly. See
        the class documentation for details.
    """
    import sdmx

    if adapt:
        source: "pathlib.Path" | "CSVAdapter" = CSVAdapter(path, **adapt)
    else:
        source = path

    return cast(
        "sdmx.message.DataMessage",
        sdmx.read_sdmx(source, format="csv", structure=structure),
    )


def fields_to_mda(
    cls: type,
    rs: "sdmx.model.v21.ReportStructure",
    cs: "sdmx.model.common.ConceptScheme | None" = None,
) -> None:
    """Populate `rs` with MetadataAttributes corresponding to dataclass fields of `cls`.

    Examples
    --------
    >>> @dataclass
    ... class MDSExample:
    ...     #: Foo
    ...     #:
    ...     #: Description of Foo.
    ...     foo: str
    ...
    ...     bar: int
    ...
    ... fields_to_mda(MDSExample)

    In this example, two metadata attributes will be added to `rs`:

    1. With id="foo" and an annotation with id="data-type" and text="<class 'str'>".
       The concept identity for the metadata attribute will also have id="foo",
       name="Foo", and description="Description of Foo."
    2. With id="bar" and an annotation with id="data-type" and text="<class 'int'>".
    """
    from sdmx.model import common, v21

    # Assemble info about the dataclass fields of `cls`
    field_info = {f.name: (f, "") for f in fields(cls)}

    # Tokenize the source code of `cls` and update `field_info` with the Sphinx-style
    # comments that precede each of the fields
    #
    # Thanks to https://davidism.com/attribute-docstrings/ and
    # https://stackoverflow.com/a/7457047
    comments = []  # Accumulate comment tokens
    for tok in generate_tokens(StringIO(dedent(getsource(cls))).readline):
        if tok.type == COMMENT:
            comments.append(tok.string.lstrip("#: "))  # Store
        elif tok.type == NAME and tok.string in field_info and len(comments):
            # Reached the definition of a field, and there are accumulated comments
            field_info[tok.string] = (field_info[tok.string][0], "\n".join(comments))
            comments = []  # Reset

    cs = cs or common.ConceptScheme()

    for id_, (f, docstring) in field_info.items():
        # Split the docstring, if any, to a name and optional description
        name, _, desc = docstring.partition("\n\n")

        # Construct the ConceptIdentity and add to `cs`
        ci = cs.setdefault(id=id_, name=name or None, description=desc or None)
        # Construct the data type annotation
        type_anno = v21.Annotation(id="data-type", text={"zxx": repr(f.type)})
        # Add the metadata attribute to the report structure
        rs.getdefault(id=id_, concept_identity=ci, annotations=[type_anno])
