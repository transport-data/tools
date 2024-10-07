.. _{{mda}}:

{{ mda }}: {{ value_id | length }} unique values
================================================

{% for value, dfd_ids in value_id | items | sort %}

{{ value }} ({{ dfd_ids | length }} appearances)
   {%+ for id in dfd_ids | sort %}{{ id }}{{ ", " if not loop.last }}{% endfor %}
{% endfor %}
