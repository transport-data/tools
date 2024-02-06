Data standards
**************

.. contents::
   :local:
   :depth: 2

About
=====

This document contains TDCI standards for the structure, format, processing, and exchange of data.

These standards:

…are *community-developed and -maintained*.
   If you are a provider or user of TDC data, you are part of this community, and your contributions are welcome and encouraged!
   To raise or propose changes to the source text of this page, you can
   `start or join a discussion <https://github.com/orgs/transport-data/discussions>`_,
   `file an issue <https://github.com/transport-data/tools/issues>`_, or
   `open a pull request <https://github.com/transport-data/tools/pulls>`_ for review.

…use key words from `RFC 2119 <https://www.rfc-editor.org/rfc/rfc2119.html>`_ to indicate *requirement levels*.
   These include words in boldface like **must** / **required**; **should** / **recommend(ed)**; and **may** / **optional**.
   Taken together, data and/or processes that fulfill all the ‘required’ standards can be considered “TDC formatted”.
   Data that also fulfill all the recommended and optional standards represent *best practices*.

…are implemented by TDCI itself.
   TDCI processes, the TDC infrastructure, the code in this :mod:`transport_data` Python package, and TDCI data products such as “TDCI Harmonized” data serve as examples for best-practice implementation of these standards.

…build on and connect to other standards (instead of duplicating or reinventing them).
   For instance, for the ``GEO`` code list, TDCI does not define a new list of codes or names, but incorporates `ISO 3166 <https://en.wikipedia.org/wiki/ISO_3166#Parts>`_ or other codes defined by larger institutions by reference.

…aim to be *complete* and *precise*.
   In practice this means the standards are quite long, and examples are deliberately kept short.
   TDCI develops and supports community development of tutorials, guides, explainers, in multiple languages and media, targeted to different audiences, that help with the adoption of these standards.
   These **must** promote a correct implementation of the standards, and **may** give more detailed and elaborate examples.

Definitions
===========

See `Concepts for transport data <https://paul.kishimoto.name/transport-data-concepts/>`__.
These reference many terms from **ISO 17369 Statistical data and metadata exchange (SDMX)** (`sdmx.org <https://sdmx.org>`_), specifically Section 2 — Information Model (SDMX-IM).
See `Standards <https://sdmx.org/?page_id=5008>`__ on the SDMX web site.

.. todo:: Incorporate that text in this page or another.

Maintainable artefact
   Any object in the information model that is associated with a Maintainer: an organization that has authority and responsibility for updating it.
   Includes, among others: data flows, data structures, and item schemes (code lists, concept schemes, agency schemes).

Upstream, downstream
   Often data is handled by a long chain of organizations and individuals;
   For instance, if Alice makes a direct measurement; Bob collects data from Alice and others; and Chen retrieves data from Bob, then:

   - Both Alice and Bob's data are **upstream** from the data handled by Chen; Bob is *directly* upstream.
   - Both Bob and Chen's data are **downstream** from the measurements made by Alice.

   Terms like ‘raw’, ‘original’, etc. should be avoided except to refer to the *ultimate* upstream data source.
   For instance, Chen may regard unaltered data from Bob as ‘original’, but this may not be the same as the data provided by Alice.

Entities
--------

TDCI
   …is the collection of people affiliated with TDC, either as individuals or representatives or organizations.

Data categories
---------------

These standards concern four broad categories of data:

Public data
   Data from open public repositories collected and aggregated by TDCI for ease of access.

   The TDC standards do not govern these data; to the contrary, TDCI processes **must** accommodate different formats etc. that result from legitimate differences in the practices of data subjects and providers.
Community data
   Data contributed directly to the TDC by TDCI participants or community members—either individuals or organizations.

   The TDC standards provide **optional** and **recommended** but *not* mandatory requirements for these data.
TDC formatted or -compliant
   Data in SDMX formats that meet the minimum requirements below.
TDCI Harmonized
   Data products prepared by the TDCI through transforming and merging data from multiple sources (including the 3 above categories), with validation and other quality control measures applied.

   These data **must** meet the mandatory, recommended, *and* optional requirements in this document.

These categories are not exhaustive: for instance, there are others including **proprietary** (non-public) data.
The TDC standards only mention these where relevant.

Structures and metadata
=======================

Maintainers
-----------

Every maintainable artifact **must** be associated with a specific maintainer.

The maintainer **must** include at least one :class:`~sdmx.model.common.Contact` with at least the :attr:`~sdmx.model.common.Contact.name`, and :attr:`~sdmx.model.common.Contact.email` attributes, for the person(s) responsible for preparing the (meta)data in TDC formats.
It **should** include additional contacts, including:

- People responsible for preparing original (meta)data.
- Authors of publications to which the data are associated.
- Fallback/organizational contacts, in case the above people leave the organization.

Where upstream data providers do not directly provide metadata or structures, and these are instead attached or inferred by TDCI, then TDCI **should** be the maintainer of those artifacts, which **should** have an ID that identifies the upstream provider.

.. admonition:: Example

   - A code list ``TDCI:CL_FOO_GEO``—maintainer ‘TDCI’ and ID ‘CL_FOO_GEO’—can signify codes used by the data provider ‘FOO’, but collated as a self-contained list by TDCI.
   - A code list ``FOO:CL_GEO``—maintainer ‘FOO’ and ID ‘CL_GEO’—can signify codes published by ‘FOO’ directly as a self-contained list.

Descriptions of artifacts **should** reiterate in plain language the exact provenance of data and structures.

Annotations
-----------

The TDCI identifies the following IDs for SDMX annotations that can be attached to any :class:`~sdmx.model.common.AnnotableArtefact`.
If used, annotations with these IDs **must** conform to the given requirements:

``tdc-concept``
   Identifies a TDC concept/dimension.
   See :ref:`dsd`, below.
``tdc-generated``
   Date, time, and version of the :mod:`transport_data` code used generate the object.

   .. admonition:: Example

      `2023-05-11T21:42:55.760130 by transport_data v0.1.dev63+g92a2aac.d20230511`

   The function :func:`.anno_generated` generates such an annotation and **should** be called on all objects created in this package.

Codes
-----

Any code list intended for reuse (with multiple data structures and flows) **should** include one or more of the following commonly-used codes, as necessary:

- ``_T``: Total, no breakdown, or a sum across all other codes.
- ``_X``: Not specified.
- ``_Z``: Not applicable.

This avoids the need to handle individual choices of words like “Total”, “TOTAL”, “ALL”, “Sum”, and their many synonyms and translations in other languages.

.. _dsd:

Data structures
---------------

Data structures that describe TDC formatted data flows **should** reflect the original or full dimensionality and attributes of the data.

TDCI Harmonized data structures **must** use the following IDs for dimensions and attributes, if they appear in data. [2]_
TDC formatted data **should** use the IDs; but if not **must** include a ``tdc-concept`` annotation that indicates one of the following, so that the data can be automatically transformed.

``GEO``
   Geographical area.
   Sometimes called "country", "region", "economy", or "ISO [3166 alpha-2 or alpha-3] code".
``TIME_PERIOD``
   Primary time dimension.
``UNIT_MEASURE``
   Units of measurement.

.. [2] These IDs follow the practice of major data providers and the SDMX Global Registry.

Data
====

TDC formatted data **must** be provided together with structure information and metadata, as described above.
In other words, an SDMX data message alone, without accompanying SDMX structure message(s) that give the structure of the data, is *not* TDC formatted.

Processes
=========

Community data
--------------

Data **should** be published in a durable archive. [1]_
Such archives may include, among others:

- `Zenodo <https://zenodo.org>`_.
- `Dryad <https://datadryad.org>`_.
- Any institutional archive that is connected to the `digital object identifier (DOI) <https://www.doi.org/the-identifier/what-is-a-doi/>`_ or `Handle <https://en.wikipedia.org/wiki/Handle_System#Design_principles>`_ systems.

Data in such archives—unlike ordinary websites—is guaranteed to be accessible and resolveable in the future, even if their exact location changes.

Providers **may** choose to publish data in more than one location; if so, they **should** minimize or prevent differences between the data available from each location, or at least clearly document those differences.
They **may** do this by linking to the durable archive.

.. [1] The TDC infrastructure will eventually serve as such an archive, but it is not yet operational.

TDC formatted data
------------------

Providers of TDC formatted data **should** develop tools or code to reproducibly, automatically convert data from their original formats to SDMX.

Such tools **should**:

- be open source and free to use.
- be concise, documented, and readable.
  One way to achieve this is to *use functions and utilities* from the :mod:`transport_data` package directly, instead of duplicating such code.
- be reproducible by the TDC and other downstream data users.
- where the original data are ambiguous (for example: tabular formats that mix key values, attribute values, and observation values), distinguish dimensions from attributes.
- where the original data provide idiosyncratic or missing IDs: apply the dimension and/or attribute IDs listed above under :ref:`dsd`.

TDC Harmonized data
-------------------

For the benefits to certain data users and groups, the TDCI develops processes to:

- transform upstream data,
- merge data from multiple sources,
- set data quality criteria,
- validate data by applying these criteria,
- calculate, derive, or synthesize new data values based on various methods,
- describe data gaps and quality.

The resulting data **may** be labelled “TDCI Harmonized”.
Even where not so labelled, derived data and quality information **must** be clearly documented
with:

- Intended user groups or audience, and
- Details of the processing steps, methods, and/or criteria applied.

If implemented in code, that code **must** be publicly available and **must not** rely on proprietary data or software.
If data processing is performed manually, the steps **must** be described in sufficient detail to allow another group or individual to independently repeat the processing and arrive at the same results.

Configurability
~~~~~~~~~~~~~~~

TDCI-developed processes **should** further:

- Be coded in a way that allows selection of parameters, metadata, collections of input data sources, and other alternatives for data processing.
- Support data users with examples and documentation in running the same processes with different settings, so as to obtain different output data.
- If possible, provide such alternate output data directly as options for user selection.

.. admonition:: Example

   Suppose a data quality criterion is that “certain sums of data from data flow ``DF1`` should be no more than 5% lower or 10% higher than reference values from data flow ``DF2``”, and a process *discards* observations from ``DF1`` that do not meet the criterion.

   The implementation of this criterion and process **should** allow users to:

   - Select other threshold values than 5% and 10%;
   - Choose another source than ``DF2`` for reference observations; or
   - Retain or annotate (instead of discarding) ``DF1`` observations that don't meet the criterion.

Modification
~~~~~~~~~~~~

When the TDCI or community members propose changes to data processes, they **should**:

- clearly advertise those changes to current users of the output data and structures,
- provide adequate advance notice, and
- invite comment and discussion by users on the changes.

The extent (duration, detail) of this consultation and notice should be proportionate to the scope of changes to be made.

As far as possible, it **must** remain possible for users to obtain or prepare data according to prior processes, so that they are not obliged to immediately adapt to any changes that are implemented.
