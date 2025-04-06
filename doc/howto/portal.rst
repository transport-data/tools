Create records using the TDC portal
***********************************

`portal.transport-data.org <https://portal.transport-data.org>`_ provides a web interface for updating and managing data and metadata in the Transport Data Commons.
This guide explains how to create high-quality records using the portal.

Introduction
============

Transport Data Commons data and metadata are stored using the free and open source CKAN software
(`documentation/user guide <https://docs.ckan.org/en/latest/user-guide.html>`_, `Wikipedia <https://en.wikipedia.org/wiki/CKAN>`__).
The website at `portal.transport-data.org`_ is a **portal** or **front end** designed to make it easy to interact with these (meta)data. [1]_

**Terminology.**

Record
   This guide uses the word **record** to refer to the individual objects contained in TDC/CKAN.
   One way to think of records is to imagine a physical, paper card in a `library catalogue <https://en.wikipedia.org/wiki/Library_catalog>`_.
   The record may contain information *about* (that is, metadata for) a library holding,
   but it is not the same thing as the actual book, magazine, or other item.
   Usually the record contains information that you can use to *locate* the actual item.

Dataset
   CKAN and (currently) the TDC portal use the word **dataset** to refer to an individual record.
   This can lead to confusion,
   because the same word is commonly used with different meanings in different contexts.
   For example:

   - Someone might say “…the ATO *dataset*…” as a colloquial way of referring to the collection of data titled `ATO National Database <https://asiantransportobservatory.org/snd/>`_.
     A second person might say “…the ATO Infrastructure (INF) *dataset*…” or “…the ATO INF-TTI-008(3) *dataset*…”
     as a way of referring to portions of the same collection of data.
   - In the context of the SDMX standards that are part of the TDCI :doc:`standards`,
     there is :ref:`a precise definition <std-defs>` of a “Dataset” as a collection of observations sharing the same structure and measure(s).

Resource
   CKAN's documentation uses this word to refer to **individual files** that are attached to a record.
   There may be zero (0) or more files for each resource.
   In the TDC portal, these appear on the “Downloads” tab of a record page,
   next to the label “Data and resources”.

Other terms
   - Upstream
   - Downstream
   - Database
   - Data provider
   - Data source

High-quality metadata, among other characteristics:

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
   …

Description
   - Write the full description (“Overview”, below) first,
     then return to fill this field.

Overview
   - Include an explicit list of all dimensions of the data,
     their IDs or names,
     and the codes, values, or labels appearing along each dimension.

Keywords
   …

Sources
   …

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
   …

Geographies
   …

Sectors
   …

Services
   …

Modes
   …

Indicator
   …

Dimensioning
   …

Data provider
   …

Data access
   …

URL
   …

Attach files
------------

Dataset files
   …

Documentation and metadata files
   …

.. [1] There is also the 'plain' CKAN interface at https://ckan.transport-data.org.
   Generally, you should not need to use this.
   The current guide shows how to perform actions through the portal/front-end.
