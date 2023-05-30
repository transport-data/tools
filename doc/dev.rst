Development
***********

The :mod:`transport_data` code is:

- **Under development**
  This means its features are not stable and may change at any time.
  For example, portions of the code may be migrated to other repositories and packages without advance notice or deprecation.
- **Unofficial.**
  The TDCI *handles* data from data providers such as :mod:`.adb`, :mod:`.jrc`, and others.
  However, the derived data products—in particular, SDMX-formatted data and structures—produced by :mod:`transport_data` are strictly unofficial and, unless explicitly stated, have not been checked or validated by the original providers.

Design goals
============

- The code is simple, modular, and flat.
- There is one module per data provider.
- Modules for different data providers have roughly similar semantics (such as function names), but these are not (for now) tightly enforced.
- Data is processed from various original formats to SDMX objects, but stored and manipulated as SDMX wherever possible.
- :mod:`transport_data` does not duplicate data, metadata, or structural information from data providers.

SDMX usage conventions
======================

The SDMX standards are deliberately crafted to be generic and broadly applicable.

In order to support convergence and harmonization of transport data, TDCI has certain conventional ways of using SDMX.

- Annotations IDs.
  :func:`anno_generated` adds an annotation to any :class:`~sdmx1.model.v21.AnnotableArtefact` with the ID ``tdc-generated``.
  This annotation contains text like "2023-05-11T21:42:55.760130 by transport_data v0.1.dev63+g92a2aac.d20230511" indicating the date, time, and version of :mod:`transport_data` code used to generate the SDMX object.
