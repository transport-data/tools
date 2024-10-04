{% macro summarize_metadatareport(report, heading="-") %}
{% set dataflow = report.attaches_to.key_values["DATAFLOW"].obj %}
.. _{{ report | dfd_id }}:

{% filter rst_heading(heading) %}Data flow ``'{{ report | dfd_id }}'`` `^ <top>`_{% endfilter %}

{% for metadata_concept in ["DATA_PROVIDER", "URL", "MEASURE", "UNIT_MEASURE", "DATA_DESCR", "COMMENT"] %}
{% set ra_value, mda = get_reported_attribute(report, metadata_concept) %}
{% if not mda %}{% continue %}{% endif %}

*{{ mda.concept_identity.name }}*: {% if metadata_concept == "DATA_PROVIDER" %}
**{{ ra_value }}**
{% elif metadata_concept == "URL" %}
`(link) <{{ ra_value }}>`__
{% elif metadata_concept == "DATA_DESCR" %}


{{ ra_value }}
{% else %}
{{ ra_value if ra_value else "*(empty)*" }}
{% endif %}
{% endfor %}

{{ summarize_dataflow(dataflow) }}
{% endmacro %}

{% macro summarize_dataflow(dfd) %}
…with dimensions:

{% for dim in dfd.structure.dimensions %}
{{ loop.index }}. **{{ dim.id }}**: {{ dim | format_desc }}
{% endfor %}
{% endmacro %}

{% filter rst_heading("*") %}{{ ref_area }} metadata and data{% endfilter %}


This file contains a summary of metadata and data for {{ ref_area }} collected through the project from the consultant team, GIZ Country Focal Points (CFPs), etc.

- It is automatically generated using the tools developed at transport-data/tools#21 on GitHub, using a command similar to:

  .. code-block::

     tdc org summarize --ref-area={{ ref_area }} “Metadata 2024-09-27.xlsx”

  …currently using, as input, the Teams file “Metadata file – prototype 1.xlsx” as of 2024-09-27.

- Use “File > Version History” in Microsoft Office to see updates.
- For questions or information please contact Paul Kishimoto via Teams and/or see the HOWTO.
- The entire file may be overwritten periodically.
  **Do not** make edits in this file if you need them to be preserved; instead, make a copy and edit there.

.. _top:

**Direct links:**

**{{ matched | length }}** data flows containing data on {{ ref_area }}:
{% for mdr in matched %}`{{ mdr | dfd_id }}`_{{ ", " if not loop.last }}{% endfor %}


**{{ no_match | length }}** other data flows:
{% for mdr in no_match %}`{{ mdr | dfd_id }}`_{{ ", " if not loop.last }}{% endfor %}


{% filter rst_heading("=") %}Data flows containing data on {{ ref_area }}{% endfilter %}


These data flows are explicitly marked as containing data pertaining to the country.

{% for mdr in matched %}
{{ summarize_metadatareport(mdr) }}
{% endfor %}


Other data flows
================

These data flows are not *explicitly* identified as containing data on the country.
This doesn't completely rule out that they *may* contain such data, but this is less likely and would require further investigation and inspection.

{% for mdr in no_match %}
{{ summarize_metadatareport(mdr) }}
{% endfor %}
