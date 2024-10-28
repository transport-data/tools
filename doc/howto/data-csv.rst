Format TDC-compliant data in CSV or SDMX-CSV
********************************************

This guide explains how to format **data** in either SDMX-CSV or other related formats supported by :mod:`.transport_data`.

Introduction
============

**Comma-separated value** (CSV) is a generic text file format.
It is standardized by IETF :rfc:`4180`; see also `Wikipedia <https://en.wikipedia.org/wiki/Comma-separated_values>`_ for more information.

- The CSV standard only describes **records** (‘rows’ or ‘lines’) and **fields** (‘columns’).
  It does not describe *what these mean or signify*.
- There are many ways to store data in CSV.
  For example, the two following CSV fragments contain the same numerical values, in different arrangements:

  .. code-block::

     MONTH, Apple,  Orange
     May,   6,      8
     May,   5,      10

  .. code-block::

     MONTH, FRUIT,  count
     May,   Apple,  6
     May,   Orange, 8
     June,  Apple,  5
     June,  Orange, 10

  However, without explicit statement of what the fields of the header and of each line signify, it is complicated or impossible to identify their meaning.
- There are many formats based on or compliant with CSV.
  Some of these are (partly or fully) standardized and well documented.
  Others are idiosyncratic to particular users or applications.

The TDC :doc:`/standards` require (see section :ref:`‘Data’ <std-data-file-format>`) that “TDC formatted/compliant” and “TDC Harmonized” data be available in an SDMX file format.

- One such file format is SDMX-CSV.
  This is not the only format.
- The `SDMX-CSV standard <https://github.com/sdmx-twg/sdmx-csv/blob/master/data-message/docs/sdmx-csv-field-guide.md>`_ gives a full specification of which fields and values should be in the header and records of a compliant CSV file.
  It also includes `many examples <https://github.com/sdmx-twg/sdmx-csv/blob/master/data-message/docs/sdmx-csv-field-guide.md#examples>`_.
- Following this standard allows data to be *automatically* parsed, interpreted, and validated against SDMX structure information.

Requirements
============

In order to follow this HOWTO, you need the following:

1. This Python package, :mod:`.transport_data` installed and usable on your system.
   See :ref:`install`.
2. Some existing data.
3. A stored **data flow definition** (DFD) for the data (2).

   This DFD, and the associated **data structure definition** (DSD), must include:

   - …

   .. note:: This HOWTO does not currently specify how to prepare a DSD and DFD.
      This will be added in the future, to this HOWTO or a separate one.

A. Choose a file format
=======================

:mod:`.transport_data` can handle the following formats:

1. SDMX-CSV (:file:`.xlsx`).

   .. code-block::

      STRUCTURE,STRUCTURE_ID,ACTION,DIM_1,DIM_2,DIM_3,OBS_VALUE
      dataflow,ESTAT:NA_MAIN(1.6.0),I,A,B,2014-01,12.4

2. A ‘reduced’ or ‘simplified’ CSV format (:file:`.csv`).
   This is not a standard SDMX format, and is only supported by :mod:`.transport_data`, which converts it into SDMX-CSV (1, above).

   It omits from SDMX-CSV the fields "STRUCTURE", "STRUCTURE_ID", and "ACTION":

   .. code-block::

      DIM_1,DIM_2,DIM_3,OBS_VALUE
      A,B,2014-01,12.4

   If you choose this format, take note of the:

   - Structure type.
     This is the value that would appear in the SDMX-CSV "STRUCTURE" field, for instance "dataflow"
   - Structure URN.
     This is the value that would appear in the SDMX-CSV "STRUCTURE_ID" field, for instance "ESTAT:NA_MAIN(1.6.0)".
   - Action.
     This is the value that would appear in the SDMX-CSV "ACTION" field, for instance "I".

3. Microsoft Excel or Office Open XML Spreadsheet (:file:`.xlsx`).
   This is not a standard SDMX format, and is only supported by :mod:`.transport_data`, which converts it into SDMX-CSV (1, above).

   It consists of SDMX-CSV (1, above) or reduced/simplified CSV format (2, above) in 1 or more worksheets in a workbook (file).

   If you choose this format, take note of the:

   - Sheet name(s).
     Your file **may** contain multiple sheets that are structured by the same, or multiple, DSDs/DFDs.

B. Format data
==============

Format data in the chosen format:

1. In the header line/record, put the following fields/columns:

   - (Only if using SDMX-CSV) ``STRUCTURE``, ``STRUCTURE_ID``, and ``ACTION``.
   - The ID of each **dimension** of the data.
     In the aboves examples, these are ``DIM_1``, ``DIM_2``, ``DIM_3``.
     These **must** match the DSD/DFD selected above, and all dimensions **must** be included.
   - The ID of the **measure** of the data.
     In most cases this will be ``OBS_VALUE``.
     This **must** match the DSD/DFD.
   - The ID of any **attributes** of the data.
     These **must** match the DSD/DFD, but some or all **may** be omitted.
   - Any additional columns (the SDMX-CSV specification calls these ‘custom columns’).
     (These will be ignored, but they **may** be present in the file.)

2. Add records.
   Transform existing data to the column order established in the previous step.
   Ensure the data do not contain any formatting errors; for instance:

   - The dimension columns do not have any empty fields/cells.
     For example, the following is invalid because there is no key value for ``DIM_2`` in the second data record:

     .. code-block::

        DIM_1,DIM_2,DIM_3,OBS_VALUE
        A,B,2014-01,12.4
        A,,2014-01,23.5
        A,D,2014-01,34.6

   - There are no extra fields/cells without corresponding labels in the header.
     For example, the following is invalid because there is no label for the column containing "FOO":

     .. code-block::

        DIM_1,DIM_2,DIM_3,OBS_VALUE,COMMENT
        A,B,2014-01,12.4,Estimated
        A,C,2014-01,23.5,Estimated,FOO

3. Save your file.

C. Check the data
=================

In this step, you will use the :program:`tdc` command-line tool to check that the data file prepared in the previous step is (a) in SDMX-CSV or a format supported by :mod:`.transport_data` and (b) aligns with the chosen DSD/DFD.

In a terminal, run a command similar to:

.. code-block:: bash

   tdc check \
     --structure=dataflow \
     --structure-id="TDCI:EXAMPLE(1.0.0)" \
     --action=I \
     --sheets=sheet_A \
     my-file.xlsx

Output is displayed similar to:

.. code-block::

   File: my-file.xlsx
   Sheet: sheet_A

   1 data set(s) in data flow Dataflow=TDCI:EXAMPLE(1.0.0)

   Data set 0: action=ActionType.information
   120 observations

…or, an error message describing any errors.
To correct the errors, you may need to:

- Return to Section B above and ensure the data are correctly formatted.
- Adjust the command-line options given.

The command-line options like :program:`--structure=dataflow` depend on the format you chose above in section A.

- For SDMX-CSV, no options are necessary.
- For simplified/reduced CSV, the :program:`--structure`, :program:`--structure-id`, and :program:`--action` options **must** be given.
  These allow :mod:`.transport_data` to convert to CSV to valid SDMX-CSV, and then read it.
- For :file:`.xlsx`:

  - The :program:`--structure`, :program:`--structure-id`, and :program:`--action` options **must** be given if the sheet(s) to be read are in the simplified/reduced format.
  - The :program:`--sheets` option **must** be given if you do not wish to check *every* worksheet in the workbook.
    Two or more sheet names *may* be given, separated columns, for example :program:`--sheets="sheet_A,sheet_B"`.
