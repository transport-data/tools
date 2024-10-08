"""Utilities for working with pycountry_.

.. _pycountry: https://pypi.org/project/pycountry/
"""

#: Mapping from country name forms appearing in data to values recognized by
#: :meth:`pycountry.countries.lookup`.
NAME_MAP = {
    "russia": "RU",  # "Russian Federation"
    "turkey": "TR",  # "Türkiye"
}
