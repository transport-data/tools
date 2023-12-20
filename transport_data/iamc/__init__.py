"""Handle data and structure for IAMC-like formats.

.. todo:: Add a function to generate distinct DSDs for each data flow in a data set.
.. todo:: Add function(s) to reshape IAMC-like data.
"""
import logging
from typing import Optional

import pandas as pd
import sdmx.model.v21 as m
from sdmx.message import StructureMessage

log = logging.getLogger(__name__)


def get_agency():
    return m.Agency(
        id="IAMC",
        name="Integrated Assessment Modeling Consortium",
        contact=[m.Contact(uri=["https://iamconsortium.org"])],
    )


def get_iamc_structures():
    """Return common metadata for IAMC-like data and structures.

    Returns
    -------
    ConceptScheme
        with id "IAMC", containing the concepts for the IAMC dimensions and attribute.
    """
    cs = m.ConceptScheme(
        id="IAMC", name="Concepts in the IAMC data model", maintainer=get_agency()
    )

    cs.extend(
        [
            m.Concept(id="MODEL", name="Model name"),
            m.Concept(id="SCENARIO", name="Model configuration or parametrization"),
            m.Concept(id="REGION", name="Geographical area"),
            m.Concept(id="VARIABLE", name="Measure and additional dimensions"),
            m.Concept(id="UNIT", name="Unit of measurement"),
            m.Concept(id="YEAR", name="Time period"),
        ]
    )

    return cs


def make_structures_for(
    data: pd.DataFrame,
    base_id: str = "GENERATED",
    maintainer: Optional[m.Agency] = None,
) -> StructureMessage:
    """Return IAMC-like data structures describing `data`.

    Parameters
    ----------
    data : pandas.DataFrame
        Data in IAMC tabular format.

        - Either long (with a "YEAR" column) or wide (no "YEAR" column but one or more
          columns with :class:`int` codes for the "YEAR" dimension).
        - Column names in any case.
          Upper-cased column names must appear in the IAMC concept scheme
          (:func:`get_iamc_structures`).

    Returns
    -------
    StructureMessage
        including:

        - The "IAMC" ConceptScheme from :func:`get_iamc_structures`.
        - A data structure definition with ID `base_id`.
        - One code list for each dimension.
        - A "MEASURE" concept scheme including the unique measures: that is, parts
          appearing before the first pipe ("|") separator in the "VARIABLE" column of
          `data`.
        - For each measure: 0 or more code lists, each containing codes for a single
          dimension in the parts of "VARIABLE" column values beyond the first pipe ("|")
          separator.
    """
    # Generic IAMC ConceptScheme
    iamc_cs = get_iamc_structures()

    # Default maintainer
    maintainer = maintainer or m.Agency(id="TEST")

    # Empty structures
    sm = StructureMessage()
    dsd = m.DataStructureDefinition(id=base_id, maintainer=maintainer)

    # Identify dimension IDs from column names
    data_format = "long"
    for name in data.columns:
        try:
            # Identify `name` as one of the standard IAMC concepts
            dim_concept = iamc_cs[name.upper()]
            dsd.dimensions.append(m.Dimension(id=name, concept_identity=dim_concept))
            continue
        except KeyError:
            pass
        try:
            # Identify `name` as an integer year label
            int(name)
            # Succeeded; add the YEAR dimension if not already added
            if "YEAR" not in dsd.dimensions:
                data_format = "wide"
                dsd.dimensions.append(
                    m.Dimension(id="YEAR", concept_identity=iamc_cs["YEAR"])
                )
        except ValueError:
            raise

    dsd.description = f"The original data are in {data_format!r} format."
    sm.add(dsd)

    # Create code lists
    for dim in filter(lambda d: d.id.upper() not in "YEAR VARIABLE", dsd.dimensions):
        cl = make_cl_for(data[dim.id], id=dim.concept_identity.id)
        cl.maintainer = maintainer
        sm.add(cl)

    # Special handling for "VARIABLE"
    for obj in make_variable_structures(data["variable"]):
        obj.maintainer = maintainer
        sm.add(obj)

    sm.add(iamc_cs)

    return sm


def make_variable_structures(data: pd.Series) -> list:
    """Make structures for IAMC-like ``Variable`` `data`.

    Returns
    -------
    list
        A sequence of SDMX structures.
    """
    # Split the data on the first "|"
    parts = data.drop_duplicates().str.split("|", expand=True)

    # A Concept scheme for the measures appearing in `data`
    cs = m.ConceptScheme(id="MEASURE")

    # Structures to be returned
    structures = [cs]

    # Identify and group by the measure in the first part
    for name, group_parts in parts.groupby(0):
        # Add the measure to the concept scheme
        measure = m.Concept(id=str(name).upper().replace(" ", "_"), name=name)
        cs.append(measure)

        # Make a DSD and code lists from the remaining parts
        # TODO also include the general (model, scenario, etc.) dimensions
        structures.extend(make_measure_structures(measure, group_parts.iloc[:, 1:]))

    log.info(
        f"Identified {len(cs)} measures from {len(parts)} distinct 'variable' values"
    )

    return structures


def make_measure_structures(measure: m.Concept, parts: pd.DataFrame) -> list:
    """Create a DSD and code lists for a particular `measure` from variable `parts`."""
    dsd = m.DataStructureDefinition(id=measure.id)

    # Structures to be returned
    structures = [dsd]

    # Drop any columns that are empty
    parts = parts.dropna(axis=1, how="all")

    # Check whether labels are balanced
    some_empty = parts.isna().any(axis=0)
    if some_empty.any():
        # commented: log information about unbalanced numbers of dimensions
        N_dim = parts.shape[1]
        N_empty = some_empty.sum()

        log.info(f"Measure {measure.id!r}")
        log.info(
            f"Variables contain uneven dimension labels: {N_dim - N_empty}–{N_dim}"
        )
        pass

    # Iterate over remaining dimensions
    for i, s in parts.items():
        # Numerical ID for this dimension
        dim_id = f"DIM_{i}"

        # Generate a code list
        cl = make_cl_for(s.dropna(), id=f"{measure.id}_{dim_id}")

        # Add a special value for missing labels "_"
        if some_empty[i]:  # type: ignore [call-overload]
            cl.append(m.Code(id="_", name="No label/missing"))
        structures.append(cl)

        # Generate a dimension that references this code list and measure
        dsd.dimensions.append(
            m.Dimension(
                id=dim_id,
                concept_identity=measure,
                local_representation=m.Representation(enumerated=cl),
            )
        )

    return structures


def make_cl_for(data: pd.Series, id: str) -> m.Codelist:
    """Make a codelist for `data` for the dimension/concept `id`."""
    cl = m.Codelist(id=id)

    for value in sorted(data.unique()):
        cl.append(m.Code(id=value))

    return cl
