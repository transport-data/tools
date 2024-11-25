What's new
**********

.. Next release
.. ============

v24.11.25
=========

- Add :mod:`.iso` (:doc:`iso`) module (:pull:`29`).
- Add :mod:`.itdp` (:doc:`itdp`) module (:pull:`28`).
- Add tools for SDMX-CSV and CSV data input (:pull:`29`).

  - :func:`.util.sdmx.read_csv` and :class:`.CSVAdapter` to read SDMX-CSV and to adapt non-standard CSV to SDMX-CSV, respectively.
  - :program:`tdc check` CLI to confirm that data can be read in this way.
  - New HOWTO :doc:`howto/data-csv` to explain usage of these features.

- Add interactive :program:`tdc edit` command-line interface for authoring SDMX data structures (:pull:`28`, :pull:`31`).

  - New HOWTO :doc:`HOWTO <howto/cli-edit>` to explain usage of these features.
- Add ``METHOD`` to the TDC metadata structure (:pull:`28`) via :data:`.org.metadata.CONCEPTS`.
- Improve processing of :doc:`adb` ATO metadata (:pull:`28`).

  - Convert attributes from ATO data sets to TDC metadata reports.
  - Extract per-series data sources for sheets where the overall source attribute is “Country Official Statistics”.

- Use :mod:`dsss.store` classes for SDMX artefact storage (:pull:`27`).

  - :class:`transport_data.store.UnionStore` is now a lightweight subclass of :class:`dsss.store.UnionStore`.
  - Add :attr:`.Config.registry_remote_url`.

v24.10.8
========

- Add tools and data for the :ref:`project-tuewas` project (:pull:`21`).

  - Add :mod:`.metadata.spreadsheet`,  :mod:`.metadata.report` submodules; expand :mod:`.metadata`.
  - Add :program:`tdc org read`, :program:`tdc org summarize`, :program:`tdc org tuewas` CLI commands.

- Add :class:`.report.Report`, a base class for generating ‘reports’ (documents derived from SDMX (meta)data) and supporting code in :mod:`.util.docutils`, :mod:`.util.jinja2` (:pull:`21`).
- Adopt :mod:`pluggy <.util.pluggy>` for plug-in hooks and implementations (:pull:`21`); use the :func:`.hooks.get_agencies` hook across existing modules.
- Add :func:`.tdc_cli`, :func:`.test_data_path` test fixtures (:pull:`21`).
- Python 3.8 support is dropped (:pull:`21`), as it has reached end-of-life.
- Add :mod:`.ipcc` (:doc:`ipcc`) module (:issue:`15`, :pull:`21`).
- Add :doc:`standards` and :doc:`roadmap` documentation pages (:pull:`9`).
- Adjust :mod:`.adb` for changes in data format in the 2024-05-20 edition of the ATO National Database (:pull:`20`, :issue:`18`).
  Document the :ref:`current file format <ato-format>` that the code supports.

v24.2.5
=======

- Add :mod:`.oica` (:doc:`oica`) module (:pull:`13`).
- Improve :mod:`.store` to handle both local and registry storage; expand :doc:`documentation <store>` (:pull:`11`).
- Add :func:`.iamc.variable_cl_for_dsd`; expand documentation of :doc:`IAM data <iamc>` (:pull:`10`).
- :mod:`transport_data` supports and is tested on Python 3.8 through 3.12 (:pull:`8`).

v23.5.11
========

Initial release
