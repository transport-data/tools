IAM Consortium
**************

The "IAMC format" or "IAMC template" refers to a variety of similar data formats with a similar structure, developed by the **Integrated Assessment Modeling Consortium (IAMC)** and
others, for data that is output from or input to integrated assessment models.
Similar DSDs are commonly used in related research.

These data structures are characterized by:

- Common dimensions, including:

  - "Model", "Scenario" —identifying a model and particular configuration of that model.
  - "Region" —geography.
  - "Year" —if in ‘long’ format; or also commonly a ‘wide’ format with one column per distinct year.
  - "Unit" —in some cases this is effectively an attribute; in other cases, it may be a dimension.
    See below.
  - "Variable" —see below.

- Combination of several data flows in the same file:

  - Codes appearing in the "Variable" dimension are strings with a varying number of parts separated by the pipe ("|") character.
  - The first (or only) part indicates the measure concept, e.g. "Population".
  - Subsequent parts are codes for additional dimensions.
    For example in "Population|Female|50—59Y", "Female" may be a code for a gender dimension, and "50–59Y" may be a code for an age dimension. The data message usually does not identify these dimensions, and separate structural information may be provided only as text and not in machine-readable formats.

- Specification of "templates" in the form of files in the same format as the data, with no observation values.
  These provide code lists for the "Variable" and sometimes other dimensions.
  These thus, more or less explicitly, specify the measures, dimensions, codes, etc. for the various data flows included.

.. include:: _api/transport_data.iamc.rst
