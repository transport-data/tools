Create records using the TDC portal
***********************************

`portal.transport-data.org <https://portal.transport-data.org>`_ provides a web interface for updating and managing data and metadata in the Transport Data Commons.
This guide explains how to create high-quality records using the portal.

Introduction
============

Transport Data Commons data and metadata are stored using the free and open source CKAN software
(`documentation/user guide <https://docs.ckan.org/en/latest/user-guide.html>`_, `Wikipedia <https://en.wikipedia.org/wiki/CKAN>`__).
The website at `portal.transport-data.org`_ is a **portal** or **front end** designed to make it easy to interact with these (meta)data. [1]_

Terminology
-----------

Record
   This guide uses the word **record** to refer to the individual objects contained in TDC/CKAN.
   One way to think of records is to imagine a physical, paper card in a `library catalogue <https://en.wikipedia.org/wiki/Library_catalog>`_.
   The record may contain information *about* (in other words: metadata for) a library holding,
   but it is not the same thing as the actual book, magazine, or other item.
   Usually the record contains information that you can use to *locate* the actual item.

Dataset, database
   CKAN and (currently) the TDC portal use the word **dataset** to refer to an individual record.
   This can lead to confusion,
   because the same word is commonly used with different meanings in different contexts.
   For example:

   - Someone might say “…the ATO *dataset*…” as a colloquial way of referring to the collection of data titled `ATO National Database <https://asiantransportobservatory.org/snd/>`_.
     A second person might say “…the ATO Infrastructure (INF) *dataset*…” or “…the ATO INF-TTI-008(3) *dataset*…”
     as a way of referring to portions of the same collection of data.
   - In the SDMX Information Model that is part of the TDCI :doc:`/standards`,
     there is :ref:`a precise definition <std-defs>` of a “Dataset” as a collection of observations sharing the same structure (dimensions, measure(s), attributes, and so on).

   Other terms like **database** also have a mix of sometimes-conflicting meanings.
   In some cases, people may use 'dataset' and 'database' interchangeably.
   In other cases, a 'database' is a collection of 'data sets'.

Resource
   CKAN's documentation uses this word to refer to **individual files** that are attached to a record.
   There may be zero (0) or more files for each resource.
   In the TDC portal, these appear on the “Downloads” tab of a record page,
   next to the label “Data and resources”.

Upstream, downstream
   These words are preferred to other words like "original", "official", etc.
   This is because data may pass through several providers in a chain of provision or provenance.

   Example:

   1. Agencies A1, A2, A3, and A4 count bicycle and pedestrian traffic using human staff or automated equipment.
   2. Data (1) are published by the statistical offices of cities B1 and B2.
   3. Data (2) are aggregated, adjusted, and republished by a national statistical office, C.
   4. A researcher D may collect and harmonize data (3) from C and other similar entities in other countries.

   While 'D' may use "official statistics" to refer data (3) or "original source" to refer to the statistical offices 'C',
   these are not unambiguous or precise descriptions:
   "official statistics" could also mean (2), and technically (1) is the "original" source in this chain of provision.

   Instead, say:

   - "(1) is the upstream source for (2)".
   - "(3) is the upstream source for (4)".
   - "(4) is one downstream use/application of (3)".

Other terms
   - Data provider
   - Data source

High-quality metadata
---------------------

Among other characteristics, metadata that is "high quality"…

- Helps make the relationships between different data clear and intelligible.
  For instance,
  if data in data set B are derived from data set A,
  good metadata will help a user understand what data from A was used, how it was manipulated or transformed, where it appears in B (and where it does not), etc.
- Is consistent, and thus easy to read,
  because the information contained by each record is arranged in the same way.
- Makes it easier for users to decide whether data meets their needs.
- Simplifies the work of transforming original data into the more interoperable “TDC formatted” and “TDCI Harmonized” :ref:`categories <std-category>`.

Create a dataset
================

Begin by gathering as much information as you can about the data you intend to record.
You can ask some of the following questions:

- Are you yourself the original creator, publisher, or provider of the data?
  Are you acting on behalf of (an)other person(s) or organization(s) who are?
  Or, are you updating a record with (meta)data *used* by yourself or the TDC community,
  but provided by someone else?
- What kind of record do you intend to create?
  This can be one of:

  - A **URL-only** record, with no files/resources.
    This is the simplest, easiest, and fastest kind of record to create.
    It serves to provide a fixed reference for an upstream source of data
    that may be used or incorporated in other data that appears in another record.
  - A **mirror** of existing data that already has an authoritative or permanent home elsewhere.
  - A record that will be the first or primary location of the given (meta)data.
  - Something different.

Fill metadata
-------------

Title
   - Use `sentence case <https://en.wikipedia.org/wiki/Letter_case#Sentence_case>`_.
   - If the original data provider gives a title for the data, this **should** match exactly.
     This makes it easier to find the record
     and confirm the correspondence with the original.
   - If the original data source is a publication,
     such as an academic journal article,
     then use the title of the article.
   - **Do not** include the name(s) (full or abbreviated) of the data provider.

Name
   The front-end automatically fills this based on what you enter in the title field.
   You **should** inspect this value
   and overwrite with something that is both intelligible and short.

   - **Do** omit connection words and common words like 'data', 'dataset', etc.

   Example: if the title is “Vehicle stock data from Transport Starter Data Kits”:

   - Auto-filled name: “vehicle-stock-data-from-transport-starter-data-kits”
   - Improved name: “tsdk-vehicle-stock”

Organisation
   This field allows you to select from existing organizations that are registered within TDC CKAN.
   Select the organization that is the **provider of the data**.
   This may differ from *your* own organization.

   - If the organization does not exist, create it. [#not-covered]_
     When creating an organization, use the same abbreviation or acronym as the organization itself uses, for instance 'UNECE', 'GIZ', or 'iTEM'.
   - In the case of data provided with or in a research publication (journal article, report, or whitepaper), you can select **Other**.

Topics
   …

Description
   - First, write the full description (“Overview”, below) of the record,
     then return to fill this field.

Overview
   - Include an explicit list of all dimensions of the data,
     their IDs or names,
     and the codes, values, or labels appearing along each dimension.
   - Include relevant information about the processes of the data provider.

     Example: “Data were available from 2006 to 2018, after which it was discontinued.”

"Is this dataset archived?"
   For the purpose of this field,
   an "archived" record is stored in TDC CKAN but *not shown* in the public listing of records.

   This might occur, for instance, if a second record is created to supersede an older record;
   then the older record could be marked 'archived' to preserve it within CKAN.

   Generally, *do not* check this box when adding new data to be shared through TDC.

Keywords
   - Use the **singular** form for nouns, phrases, and terms.
     Examples:

     - "inland waterway", not "inland waterways".
     - "bus", not "buses".

Sources
   - Indicate the *immediate upstream sources* of the data collected in the record.
     If there are already TDC CKAN records for these sources,
     use the TDC URLs in the "Link (optional)" field.

     Then, in the "Overview" field, give (or link to) a *complete* description of the upstream source(s),
     as given by the data provider.

   - If the data provider has collected the data themselves,
     use a short phrase that indicates *how* the data was collected
     —in other words, the *method* of data collection.
     Then, in the "Overview" field, give (or link to) a *complete* description of the method,
     as given by the data provider.

     Example: "traffic counting"

Comments
   …

Update frequency
   …

TDC category
   …

Units
   Enter the units of measurement for instance kg.

Language
   …

Reference period
   Due to :portal-issue:`230`,
   the portal does not accept periods expressed using only the year.
   For such periods, enter January 1 on the first year and December 31 on the final year of the period.

   Example: for "1990–2023", enter "January 1st, 1990" to "December 31st, 2023".

Geographies
   …

Sectors
   …

Services
   …

Modes
   …

Indicator
   Use the **exact name** of the measure or indicator given by the data provider.

Dimensioning
   Identify **all** dimensions of the data, along with the *scope*, *resolution*, and/or *representation* of codes or labels along each dimension.

   If the data provider gives an *ID*, *name*, and/or *description* of each dimension, reproduce these exactly.
   If not, you **may** use one of the IDs provided in :ref:`this table <howto-metadata-common-concept-ids>`.

   Write each dimension on a separate line, using a numbered or bulleted list.
   Example 1::

      - Year of construction
      - Carrying capacity

   Example 2::

      1. MODE (transport mode): one of ROAD, RAIL, or WATER
      2. COMMODITY (commodity type): 41 distinct codes
      3. "Region" (GEO): see https://example.com/list-of-regions

Data provider
   Enter the **full name** followed by any official **abbreviation** in parentheses.

   Example: Transport Data Commons Initiative (TDCI)

   If the "Organization" (above) to which the record is associated is the same as the data provider,
   these **should** be identical and may be copy-pasted.

Data access
   …

URL
   As far as possible, a URL should link **directly** to a page or anchor for the record,
   on a website maintained by the data provider.

   If it is not possible to provide such a link,
   add to the "Overview" field specific steps that describe how to access the upstream data set via the URL.

Attach files
------------

Dataset files
   …

Documentation and metadata files
   …

.. [1] There is also the 'plain' CKAN interface at https://ckan.transport-data.org.
   Generally, you should not need to use this.
   The current guide shows how to perform actions through the portal/front-end.
.. [#not-covered] Not currently covered by this HOWTO.
