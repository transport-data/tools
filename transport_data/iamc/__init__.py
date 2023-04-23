"""Handle data and strucutre for IAMC-like formats.

The "IAMC format" or "IAMC template" refers to a variety of similar data formats with a
similar structure, developed by the Integrated Assessment Modeling Consortium (IAMC) and
others, for data that is output from or input to integrated assessment models. Similar
DSDs are commonly used in related research.

These data structures are characterized by:

- Common dimensions, including:

  - "Model", "Scenario" —identifying a model and particular configuration of that model.
  - "Region" —geography.
  - "Year" —if in ‘long’ format; or also commonly a ‘wide’ format with one column per
    distinct year.
  - "Unit" —in some cases this is effectively an attribute; in other cases, it may be a
    dimension. See below.
  - "Variable" —see below.

- Combination of several data flows in the same file:

  - Codes appearing in the "Variable" dimension are strings with a varying number of
    parts separated by the pipe ("|") character.
  - The first (or only) part indicates the measure concept, e.g. "Population".
  - Subsequent parts are codes for additional dimensions. For example in
    "Population|Female|50—59Y", "Female" may be a code for a gender dimension, and
    "50–59Y" may be a code for an age dimension. The data message usually does not
    identify these dimensions, and separate structural information may be provided only
    as text and not in machine-readable formats.

- Specification of "templates" in the form of files in the same format as the data, with
  no observation values. These provide code lists for the "Variable" and sometimes other
  dimensions. These thus, more or less explicitly, specify the measures, dimensions,
  codes, etc. for the various data flows included.

.. todo:: Add a function to generate distinct DSDs for each data flow in a data set.
.. todo:: Add function(s) to reshape IAMC-like data.
"""
import pandas as pd
import sdmx.model.v21 as m
from sdmx.message import StructureMessage


def get_iamc_structures():
    """Return common metadata for IAMC-like data and structures."""
    cs = m.ConceptScheme(id="IAMC", name="Concepts in the IAMC data model")

    cs.items = [
        m.Concept(id="MODEL", name="Model name"),
        m.Concept(id="SCENARIO", name="Model configuration or parametrization"),
        m.Concept(id="REGION", name="Geographical area"),
        m.Concept(id="VARIABLE", name="Measure and additional dimensions"),
        m.Concept(id="UNIT", name="Unit of measurement"),
        m.Concept(id="YEAR", name="Time period"),
    ]

    return cs


def make_dsd_for(data: pd.DataFrame) -> m.DataStructureDefinition:
    """Return IAMC-like data structures describing `data`."""
    # Generic IAMC ConceptScheme
    iamc_cs = get_iamc_structures()

    # Empty structures
    sm = StructureMessage()
    dsd = m.DataStructureDefinition(id="GENERATED")

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

    # Create code lists
    for dim in filter(lambda d: d.id.upper() not in "YEAR VARIABLE", dsd.dimensions):
        sm.add(make_cl_for(data[dim.id], id=dim.concept_identity.id))

    # Special handling for "VARIABLE"
    sm.add(make_variable_cl(data["variable"]))

    sm.add(dsd)

    return sm


def make_variable_cl(data: pd.Series) -> m.Codelist:
    """Make a `VARIABLE` codelist for `data`."""
    cl = m.Codelist(id="MEASURE")

    # Split the data on the first "|"
    for value in sorted(data.str.split("|", expand=True)[0].unique()):
        cl.append(m.Code(id=value))

    return cl


def make_cl_for(data: pd.Series, id: str) -> m.Codelist:
    """Make a codelist for `data` for the dimension/concept `id`."""
    cl = m.Codelist(id=id)

    for value in sorted(data.unique()):
        cl.append(m.Code(id=value))

    return cl
