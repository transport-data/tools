Asian Development Bank
**********************

This module handles the `Asian Transport Outlook (ATO) <https://asiantransportoutlook.com>`_ source maintained by the Asian Development Bank (ADB, initially) and Asian Infrastructure Investment Bank (AIIB, more recently), specifically the `ATO National Database <https://asiantransportoutlook.com/snd/>`_.

In particular, it converts data from the :ref:`ATO native Excel file format <ato-format>`—both the 2022-10-07 and 2024-05-20 formats—to SDMX and extracts metadata.

.. _ato-format:

ATO National Database format
============================

The ATO native Excel file format is characterized by the following.
There is an `ATO National Database User Guide <https://asiantransportoutlook.com/snd/snd-userguide/>`_ that contains some of the information below, but does not describe the file format.

- Data flow IDs like ``TAS-PAT-001(1)``, wherein:

  - ``TAS`` is the ID of a ‘category’ code with a corresponding name like “Transport Activity & Services”.
    Individual files (‘workbooks’) contain data for flows within one category.
  - ``PAT`` is the ID of a ‘subcategory’ code with a corresponding name like “Passenger Activity Transit”.
  - ``001(1)`` is the ID of an ‘indicator’ code with a corresponding name like “Passengers Kilometer Travel - Railways”.
  - All data flows with the same initial part like ``TAS-PAT-001`` contain data for the same *measure*.
    The final part ``(1)`` indicates data from alternate sources for the same measure.
- Files contain a “TOC” sheet and further individual sheets.
  See :func:`~.adb.read_sheet`, which reads these sheets, for a detailed description of the apparent format.
- The files are periodically updated.
- The update schedule is not fixed in advance.
- Previous versions of the files do not appear to be available.
- The file metadata contains a "Created by:" field with information like "2022-10-07, 11:41:56, openpyxl".
  At least two different dates have been observed:

  - 2022-10-07
  - 2024-05-20.

.. include:: _api/transport_data.adb.rst
