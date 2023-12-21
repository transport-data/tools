.. From https://stackoverflow.com/a/62613202/2362198

.. {{ (":mod:`." + fullname.split(".", maxsplit=1)[1] + "` " + objtype) | underline(line="*") }}

Code reference
==============

.. currentmodule:: {{ fullname }}

.. automodule:: {{ fullname }}

   {% block modules %}
   {% if modules %}
   .. rubric:: Submodules

   .. autosummary::
      :toctree:
      :template: autosummary/module.rst
      :recursive:
   {% for item in modules %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: Module data

   .. autosummary::
   {% for item in attributes %}
      {{ item }}
   {%- endfor %}

   {% for item in attributes %}
   .. autodata:: {{ item }}
   {%- endfor %}

   {% endif %}
   {% endblock %}

   {% block functions %}
   {% if functions %}
   .. rubric:: {{ _('Functions') }}

   .. autosummary::
   {% for item in functions %}
      {{ item }}
   {%- endfor %}

   {% for item in functions %}
   .. autofunction:: {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}
   .. rubric:: {{ _('Classes') }}

   .. autosummary::
   {% for item in classes %}
      {{ item }}
   {%- endfor %}

   {% for item in classes %}
   .. autoclass:: {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block exceptions %}
   {% if exceptions %}
   .. rubric:: {{ _('Exceptions') }}

   .. autosummary::
   {% for item in exceptions %}
      {{ item }}
   {%- endfor %}

   {% for item in exceptions %}
   .. autoexception:: {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}
