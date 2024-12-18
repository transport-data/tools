Record and update TDC-structured metadata
*****************************************

This guide explains how to record and update **metadata** in a TDC-specific file format. [1]_

.. [1] The guide was developed as part of a project funded by :doc:`/giz` under the `TUEWAS Asia <https://tuewas-asia.org>`_ network.

Introduction
============

This HOWTO does *not* set out to give a comprehensive explanation of data and metadata.
For more information, you could consult some of the references linked under :ref:`std-defs` on the page :doc:`/standards`.

What is metadata?
-----------------

Metadata is **facts or information about data**, distinct from the *data itself* (i.e. particular numbers).
By recording, exchanging, and analyzing metadata, it is possible to understand and make decisions about data processing and usage—even *without* the actual data.

Two kinds of metadata
---------------------

We are concerned with two kinds of metadata.

**Structural metadata**, as the name implies, give information about the *structure* of data.
For example, suppose we know that:

   In data set ‘X’, individual observations look like: in Canada, in 2023, 17.4 million apples and 13.8 million bananas were sold.

We could describe the structure of this data by saying:

- The data have 3 conceptual **dimensions**: country, time period, and kind of fruit.
- One dimension refers to *countries*—perhaps with labels like “Canada” (literally), or perhaps with short **codes** like “CA”.
  These codes might form a certain, fixed, **code list**: *only* the codes in this list appear in the ‘country’ dimension.

  This information also can tell us about the **scope** and **resolution** of the data, along this particular dimension.
  For example, the very name or ID of this dimension, ‘country’, implies the spatial resolution of the data: entire countries.
  Or, if the ‘country’ code list includes (CA, MX, US), we understand the spatial scope of the data is “North America”.

- A second dimension refers to the *time period*.
  As with the ‘country’ dimension, we can understand the temporal resolution (here, probably years/annual) and scope (at least the year 2023 is included; perhaps also other years).
- A third dimension refers to *kinds of fruit*.
  We see the scope is, at least, ‘apples’ and ‘bananas’.
  We might also infer that there is no further resolution related to ‘kind of fruit’: for example, the data may not distinguish “honey crisp apple” from “Fuji apple”.
- We also see that the values are for a specific **measure**.
  In this case, the measure is “number pieces of fruit were sold”.
  The same real-world activity can be measured in different ways.
  For example, fruit sold could also be measured as “total market value”, in **units of measurement** such as “US dollars equivalent at market exchange rates”.

If structural metadata explain the ‘what’ of data (answering the question: “What do the data consist of?”), then **provenance metadata** is a general term for other information about *who* provides data; *how* data is collected, prepared, and published; *when* these things happen; and *where* the data can be found.

How are metadata described, stored, and exchanged?
--------------------------------------------------

Once we have a metadata fact like, “Data set ‘A’ is published by the United Nations,” (Fact 1) we have to decide how to store this, exchange it, and compare it along with possibly many other pieces of metadata.

This is most commonly done as plain text.

TDC follows the **SDMX** standards for **Statistical Data and Metadata eXchange**.
Describing and storing metadata in a standards-based way allows to be clear and precise about its meaning.
For example, suppose we have a second fact, expressed as plain text: “Data set ‘B’ is UN data.”

- Is Fact 2 the same as Fact 1, only phrased differently?
- Or are they diffent?
  For example, is data set B “published by” a different agency than the UN, but contains “UN data” from UN data flows?

By specifying SDMX **metadata attributes** and giving distinct **metadata values** for each, we try to reduce or eliminate this ambiguity.
In this example, we can distinguish *the identity of the data provider/publisher* from *the ‘upstream’ source of the data contained in the data flow*.

These standards specify ways to describe and exchange metadata in different **file formats** that are machine-readable, such as `XML <https://en.wikipedia.org/wiki/XML>`_, JSON, and CSV.
Using machine-readable formats allows for semi-automated processing that can handle large amounts of (meta)data.

XML and JSON, however, are not easily **human-readable**.
For this reason, there are

For example, see https://ec.europa.eu/eurostat/cache/metadata/en/avia_if_esms.htm

- This file contains metadata expressed in a human-readable HTML format.
- Click “Download” at the above URL, or access https://ec.europa.eu/eurostat/api/dissemination/files?file=metadata/avia_if_esms.sdmx.zip
- This archive contains:

  - The same :file:`.htm` file.
  - Two :file:`.xml` files giving the metadata specification (:file:`ESMS_MSD.msd.xml`) and the actual metadata for this data flow (:file:`avia_if_esms.sdmx.xml`).
  - A spreadsheet in Office Open XML (“Microsoft Excel”) format with an alternate, human-readable format (:file:`avia_if_esms.xlsx`)

Understand the TDC metadata format
==================================

TDC uses an an unofficial, prototype format for metadata.
This loosely imitates the above-mentioned Eurostat format.
These files contain metadata (information *about* data) based on the SDMX information model, but their file type (.xlsx) and layout (sheet names, columns, etc.) is not specified by the SDMX standard, hence ‘unofficial’.

The files have the following sheets:

“README”
   Repeats information from this section of the HOWTO.

“Attributes”
   - One row per metadata attribute (or 'field').
   - Columns for the name; description; and ID (short and machine-readable) of each attribute.
     See these descriptions to learn what to write for each attribute.

One or more additional sheets named, e.g. “XX001”
  - The name (or title) of each sheet corresponds to the identity (ID) of the data flow that is described by the metadata in that sheet.
  - In Column A, the name of the metadata attribute.
    Each name **must** exactly match one appearing in the "Attributes" sheet.
  - In Column B, the actual metadata values.
    These **may** be empty, but **should** contain some indication of why the metadata value is not available or recorded.

“TEMPLATE”
   To add information about additional data flows not included in existing sheets (above), you can copy and rename this sheet.

Record and update metadata
==========================

- Metadata will be provided as one or more spreadsheets.
  These may be in a web-based, common, editable document, or as e-mail attachments, etc.
- Communicate clearly about which files are exchanged or edited.
- If files are not in a web-based, common, editable format, use “track changes” features in documents to distinguish your edits from existing comments.

Update or correct existing sheets
---------------------------------

- Identify and change incorrect metadata.
- If reviewing existing metadata, update the “Comment” field even if all metadata appear correct.
- Preface comments with your initials or other identifying mark and, if necessary, the date.
  For example:

     ABC (2024-08-11) Added UNIT_MEASURE.
     XY (2024-09-12) Expanded DATA_DESC; corrected URL.
     MN (2024-11-18) Check & confirmed.

Add additional sheets
---------------------

- Duplicate either “TEMPLATE” or any other existing sheet.
- Choose a new, distinct ID for the data flow.
- Be detailed!
  The ``DATA_DESC`` attribute is intended as a catch-all; use blank lines to separate different points of information about the data flow.
- Use simple language.

Use common IDs for concepts/dimensions
--------------------------------------

- If a similar concept, dimension, or code list appears in metadata for multiple data flows, try to use the same ID to identify these.
- Some known concepts/dimensions are listed below.
- If there are important distinctions with an existing concept ID—for example, if two data providers use the same name to mean very different things—add extra text in the ``DIMENSION``, ``DATA_DESC`` or other fields to explain.

================== ===
ID                 Possible values
================== ===
ACCIDENT_TYPE      e.g. fatal accidents, non-fatal injury accidents, injury accidents, vehicle damage only accidents
DESTINATION        e.g. urban, rural
DRIVER_PASSENGER   e.g. driver, passenger
FUEL_TYPE          e.g. electric, petrol
GEO; REF_AREA      Specific countries or regions
IMPORT_REG         e.g. new import, first registration, used import
INJURY_TYPE        e.g. killed, injured
INSTITUTION        e.g. government, private firm, individual
MANUFACTURER       e.g. Renault, Toyota
MODE               e.g. road, rail
NEW_USED           new; used
PUBLIC_PRIVATE     public; private
ROAD_CONDITION     e.g. paved, unpaved
ROAD_TYPE          e.g. motorway, highway
ROAD_USER          e.g. pedestrian, four-wheeled vehicle
SERVICE            freight; passenger
SEX                e.g. female; male; other
SOURCE             (of revenue) e.g. toll, tax
TIME_PERIOD
TYPE_OF_SPEND      e.g. construction, maintenance
VEHICLE_AGE
VEHICLE_TYPE       e.g. passenger car, bus, scooter
================== ===

Avoid common ‘gotchas’
======================

When handling metadata, there are some common issues that can arise.
This section lists a few, and appropriate responses.

Large/composite “databases”
---------------------------

Often, the term “data set” is use informally to refer to a collection of many kinds of data.
An easy way to notice this happening is to see if each metadata attribute has a complicated value or multiple values.

For example:

  Measure: GDP; population.

  Unit of measure: 2020 U.S. dollars; millions of people.

  Dimensions: time and country; time, country, sex, and age.

In this example, we see there are in fact **two** data flows.
It is simpler to describe these separately.
If other metadata values for one data flow are identical to the values for another, make such a reference:

   Data description: Same as [DF00X].

Mixing measures and dimensions: the word “by”
---------------------------------------------

For example:

- Data set A may be described as “Sales of cars by manufacturer”
- Data set B may be described as “Sales of cars by weight class”

In this case, the word **“by”** is a clue that *the data have at least one specific dimension*.
For data set A, that specific named dimension is “manufacturer”.
For data set B, the dimension is “weight class”.

However:

- Both data sets actually capture *the same measure*—sales of cars—and may use the same units of measurement.
- Each data set probably has additional dimensions, besides the one singled out in the name or title.
  For example, both data flow A and data flow B may have GEO and TIME_PERIOD dimensions.
  It is possible that data flow B *also* has a “manufacturer” dimension, but this is merely omitted from the name or title.

To avoid this ambiguity is to:

- Always give the complete list of dimensions.
- Do not combine dimensions with the measure.
- Avoid mentioning just one or a few dimensions.

Mixing measures and units of measure
------------------------------------

For example:

- For data flow A, the measure is given as “passenger miles traveled”.
- For data flow B, the measure is given as “passenger kilometres”.

With the above information, we can understand that these are *the same measure* (one we might call “passenger distance traveled”), but the *units of measurement* are different (in one case, miles; in the other, kilometres).
