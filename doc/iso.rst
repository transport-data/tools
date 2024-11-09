International Organization for Standardization (ISO)
****************************************************

This module provides SDMX structures based on code lists ultimately maintained by the ISO.

The ISO does *not* provide SDMX (meta)data directly.
Rather:

- The Debian `pkg-isocodes <https://salsa.debian.org/iso-codes-team/iso-codes>`_ provides these lists and their translations into at least 159 languages.
- These are mirrored and exposed in Python by `pycountry <https://github.com/pycountry/pycountry>`_.
- The current module, :mod:`.transport_data.iso`, converts these into SDMX.

The resulting code lists have SDMX URNs like ``Codelist=ISO:3166-1_alpha_2(24.6.1)`` that combine the ISO standard number (in the example, ``3166-1``); the field from the upstream data that is used for the code IDs (``alpha_2``), and a version number that is derived from the version of :mod:`pycountry` (``24.6.1``).
Thus:

- In ``Codelist=ISO:3166-1_alpha_2(24.6.1)``, the code for the country Canada has ID ``CA``.
- In ``Codelist=ISO:3166-1_alpha_3(24.6.1)``, the code for the country Canada has ID ``CAN``.
- In ``Codelist=ISO:3166-1_numeric(24.6.1)``, the code for the country Canada has ID ``124``.

The pycountry README states:

   **Data update policy**:
   No changes to the data will be accepted into pycountry.
   This is a pure wrapper around the ISO standard using the `pkg-isocodes` database from Debian *as is*.
   If you need changes to the political situation in the world, please talk to the ISO or Debian people, not me.

In the same way, :mod:`.transport_data.iso` *only* provides conversion to SDMX, and the converted code lists will not be modified to add, remove, or modify codes.
Instead, data providers who wish to use code lists derived from the ISO lists can do so by reference.
For example:

.. code-block:: Python

   from copy import deepcopy

   from sdmx.model import common
   from transport_data import STORE

   # Retrieve the code list with ISO 3166-1 alpha-2 codes,
   # their translations and annotations
   cl_iso = STORE.get("Codelist=ISO:3166-1_alpha_2(24.6.1)")

   # Create a new code list
   cl = common.codelist(id="GEO_CUSTOM")

   # Copy 1 or more codes from the ISO list; give each an
   # annotation like "urn…Code=ISO:3166-1_alpha_2(24.6.1).AW"
   # that clearly associates it with the original
   for id_ in ("AW", "ZE"):
       c = deepcopy(cl_iso.get(id_))
       c.annotations.append(
           common.Annotation(id="same-as", text=c.urn)
       )
       cl.append(c)

   # Add other code(s) not in the ISO standard
   cl.append(
       common.Code(id="XX", name="Custom code not in ISO 3166-1")
   )

.. todo:: Possibly update this submodule to load data directly from the Debian iso-codes repo, instead of via :mod:`pycountry`.

.. include:: _api/transport_data.iso.rst
