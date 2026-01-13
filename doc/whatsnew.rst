What's new
**********

Next release
============

- :mod:`transport_data` supports and is tested on
  `Python 3.14 <https://www.python.org/downloads/release/python-3140/>`_ (:pull:`51`),
  released 2025-10-07.
  Support for Python 3.9 is dropped, as it has reached end-of-life.
- Improve :mod:`.org` (:pull:`38`):

  - New CLI command :program:`tdc ckan` (see :func:`.ckan.main`).
  - New class :class:`.TDCALLReportStructure`,
    representing the contents of a TDC metadata report.
  - New functions :func:`~.org.ckan.get_msd`,
    :func:`~.org.ckan.ckan_package_to_mdr`, and
    :func:`~.org.ckan.mdr_to_ckan_package`.

  - Improve :mod:`.util.ckan` (:pull:`38`):

  - New :class:`.ModelProxy` class :class:`~.ckan.User`.
  - New method :meth:`.ModelProxy.get`.
  - :class:`.ModelProxy` processes collections of JSON objects to :mod:`transport_data` instances.
  - New class :class:`.CKANMetadataReportStructure`,
    representing the metadata fields of a CKAN package.

- Improve :class:`~.util.pooch.Pooch` class (:pull:`50`, :pull:`56`).

  - Use a secret stored with :program:`keyring set transport-data api-token-zenodo`,
    if available,
    to avoid Zenodo rate limiting.
  - Reduce repeated API calls.
  - Handle 429 Too Many Requests HTTP responses.

- :mod:`.ato` data provider:

  - Rename :py:`.adb` to :mod:`.ato` (:pull:`47`).
  - Update known hashes for files provided by :mod:`.ato` (:issue:`46`, :pull:`47`, :pull:`50`, :pull:`56`).
  - Fetch source data from Zenodo mirror (:pull:`50`, :pull:`56`).

- :mod:`oica` data provider:
 
  - Update base URL and registry per 2025-10 OICA website refresh (:pull:`56`).
  - Add 2024 data files (:pull:`56`).

- New CLI command :program:`tdc test wipe` (:pull:`38`):
- New function :func:`.util.sdmx.fields_to_mda` (:pull:`38`).
- :mod:`transport_data` supports type checking of its use in downstream code,
  by `including a py.typed marker <https://typing.python.org/en/latest/spec/distributing.html#packaging-type-information>`__.
- New HOWTO :doc:`Create records using the TDC portal <howto/portal>` (:pull:`45`).

v24.12.29
=========

- Add :mod:`.util.ckan` (:pull:`35`),
  including a :class:`~.ckan.Client` for access to CKAN instances
  (including the TDC instances);
  proxy classes for CKAN objects including :class:`~.ckan.Package`, :class:`~.ckan.Resource`, and more.
- Add :data:`.org.ckan.PROD` and :data:`.org.ckan.DEV` instances of :class:`.ckan.Client` (:pull:`35`).
- Improve documentation (:pull:`40`).

v24.11.25
=========

- Add :mod:`.iso` (:doc:`iso`) module (:pull:`29`).
- Add :mod:`.itdp` (:doc:`itdp`) module (:pull:`28`).
- Add tools for SDMX-CSV and CSV data input (:pull:`29`).

  - :func:`.util.sdmx.read_csv` and :class:`.CSVAdapter` to read SDMX-CSV and to adapt non-standard CSV to SDMX-CSV, respectively.
  - :program:`tdc check` CLI to confirm that data can be read in this way.
  - New HOWTO :doc:`howto/data-csv` to explain usage of these features.

- Add interactive :program:`tdc edit` command-line interface for authoring SDMX data structures (:pull:`28`, :pull:`31`).

  - New HOWTO :doc:`Edit data structures with the tdc CLI <howto/cli-edit>` to explain usage of these features.
- Add ``METHOD`` to the TDC metadata structure (:pull:`28`) via :data:`.org.metadata.CONCEPTS`.
- Improve processing of :doc:`adb` ATO metadata (:pull:`28`).

  - Convert attributes from ATO data sets to TDC metadata reports.
  - Extract per-series data sources for sheets where the overall source attribute is “Country Official Statistics”.

- :mod:`transport_data` supports Python 3.13 (:pull:`32`).
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
