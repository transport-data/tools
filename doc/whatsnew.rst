What's new
**********

Next release
============

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
