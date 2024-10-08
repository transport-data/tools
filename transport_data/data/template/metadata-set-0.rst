.. _top:

Metadata summary
****************

This file contains a summary of metadata collected through the project from the consultant team, GIZ Country Focal Points (CFPs), etc.

- It is automatically generated using the tools developed at transport-data/tools#21 on GitHub, using a command similar to:

  .. code-block::

     tdc org read “Metadata 2024-09-27.xlsx”

  …currently using, as input, the Teams file “Metadata file – prototype 1.xlsx” as of 2024-09-27.

- Use “File > Version History” in Microsoft Office to see updates.
- For questions or information please contact Paul Kishimoto via Teams and/or see the HOWTO.
- The entire file may be overwritten periodically.
  **Do not** make edits in this file if you need them to be preserved; instead, make a copy and edit there.


**Direct links:**

`DATA_PROVIDER`_ —
`MEASURE`_ —
`UNIT_MEASURE`_ —
`Dimensions`_

{# Write out pre-generated reports on MetadataAttributes #}
{% for obj in mda %}

{{ obj | safe }}
{% endfor %}

_`Dimensions`: {{ dim_id | length }} unique concepts
=================================================

{% for value, dfd_ids in dim_id | items | sort %}

{{ value }} ({{ dfd_ids | length }} appearances)
   {%+ for id in dfd_ids | sort %}{{ id }}{{ ", " if not loop.last }}{% endfor %}
{% endfor %}
