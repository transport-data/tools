(Meta)data storage
******************

:mod:`transport_data.store` provides for storing and handling two kinds of data files:

Local data
   Data that exist only on an individual user's system.
   These may include:

   - Cached files such as those downloaded from particular network locations.
   - Temporary or intermediate data files produced or used by other code in :mod:`transport_data` or downstream packages.

   These data are handled by an instance of the :class:`.LocalStore` class.

Maintained data
   These are data that may be distributed and referenced by other users and SDMX data or structures.
   They are handled by an instance of the :class:`.Registry` class.

:data:`transport_data.STORE` is an instance of the :class:`.UnionStore` class, which dispatches operations to :class:`.LocalStore` or :class:`.Registry` according to the maintainer of objects.
All three classes are subclassed of :class:`.BaseStore` and share a common interface.

.. _store-layout:

Formats and layout
==================

- Files are stored in the (configurable) directory indicated by :attr:`.Config.data_path`.
  This defaults to the :ref:`platformdirs:api:user data directory`.
  For instance, on a Unix/Linux system, the data may be in :file:`$HOME/.local/share/transport-data/`.

  - :class:`.LocalStore` files are in a :file:`…/local/` subdirectory.
  - :class:`.Registry` files are in a :file:`…/registry/` subdirectory.

- All files are stored as SDMX-ML (XML).

  Every SDMX :class:`~sdmx.model.common.MaintainableArtefact` has a `uniform resource name (URN) <https://en.wikipedia.org/wiki/Uniform_Resource_Name>`__ that resembles ``urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TEST:COLOUR(1.2.3)``.
  In this example:

  - "TEST" is the :attr:`~sdmx.model.common.IdentifiableArtefact.id` of a :class:`~sdmx.model.common.Agency` stored as the :attr:`~sdmx.model.common.MaintainableArtefact.maintainer` attribute.
  - "COLOUR" is the ID of the object itself.
  - "(1.2.3)" is the :attr:`~sdmx.model.common.VersionableArtefact.version` attribute of a :class:`~sdmx.model.common.VersionableArtefact`.

- Directory and file names include maintainer ID, object class name, and object ID.
  For instance, the file :file:`TEST/Codelist_TEST_COLOUR.xml` contains the :class:`~sdmx.model.common.Codelist` with ID "COLOUR" maintained by the agency with ID "TEST".
- Each file contains **only** objects of the class, ID, and maintainer corresponding to its path.
- Each file **may** contain *multiple versions* of objects.
  For instance, the file :file:`TEST/Codelist_TEST_COLOUR.xml` may contain objects with the URNs and versions:

  - ``urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TEST:COLOUR(1.0.0)`` → version 1.0.0;
  - ``urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TEST:COLOUR(1.2.3)`` → version 1.2.3;
  - ``urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TEST:COLOUR(1.2.4)`` → version 1.2.4;
  - and so on.

.. include:: _api/transport_data.store.rst
