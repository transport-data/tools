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
- There is one module per data provider (e.g. :mod:`.adb`, :mod:`.estat`, :mod:`.jrc`).

  - This makes possible the process that:

    - TDCI develops an initial or prototype module for (meta)data from a provider.
    - The provider decides to take over maintenance/development of that code.
    - The module is excised from :mod:`transport_data`, along with all code in its particular subdirectory; the code is adjusted to depend on :mod:`transport_data`.

  - Modules for different data providers have roughly similar semantics (such as function names), but these are not (for now) tightly enforced.
- Code for handling a specific format is collected in a single module, e.g. :mod:`.iamc`, and reused from there.
- Data is processed from various original formats to SDMX objects, but stored and manipulated as SDMX wherever possible.

  - SDMX :class:`~.sdmx.model.common.MaintainableArtefact` are exchanged between modules.
- :mod:`transport_data` does not duplicate data, metadata, or structural information from data providers.
  Wherever possible, these are processed from original sources.
  :mod:`transport_data` only adds metadata where it is missing in these original sources.
- As little as possible workflow/orchestration code is created.
  The individual functions/CLI commands in :mod:`transport_data` are kept generic, so they can eventually be incorporated as atomic workflow elements in a framework to be chosen later, or on the backend of the TDC web UI and other systems.

SDMX usage conventions
======================

→ moved to :doc:`standards`.

Code style
==========

- Version as ``vYY.M.D`` using the current date.
- Use `pre-commit <https://pre-commit.com>`__, which invokes `ruff <https://docs.astral.sh/ruff/>`__ for code formatting and `mypy <https://mypy.readthedocs.io/en/stable/>`__ for static type checking of Python code.
- Use `Pytest <https://docs.pytest.org>`__ for writing :mod:`.tests`.
- Write documentation in `reStructuredText <https://docutils.sourceforge.io/rst.html#reference-documentation>`__.
