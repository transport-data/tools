Edit data structures with the :program:`tdc` CLI
************************************************

.. contents::
   :local:

Introduction
============

This guide explains how to use the :program:`tdc edit` command-line interface (CLI) to edit SDMX structural artefacts.

These artefacts (for example, data structure definitions, data flow definitions, code lists, concept schemes, etc.) are usually recorded in the SDMX-ML format (based on XML, or Extensible Markup Language).
This format is both machine- and human-readable, but it is not very user-friendly or easy to edit manually.

:program:`tdc edit` provides one rudimentary, interactive way to generate and store SDMX-ML containing SDMX artefacts.
These can then be used with other, TDC-compliant (meta)data.
For example, one can define a data structure definition, and then use it to read an SDMX-CSV file that is :doc:`formatted accordingly </howto/data-csv>`.

Create a new SDMX artefact
==========================

This is currently the only feature provided by :program:`tdc edit`.

1. Start by ensuring you have :mod:`.transport_data` :ref:`installed <install>`.

2. Run :program:`tdc edit`.

   A full-screen command-line interface is shown:

   - At the top is some information about what is happening, and the artefact you are editing.
   - Below the line is a prompt.
     Always read the prompt text carefully.
   - At the bottom is a reminder that you can **press Control-C at any time to exit**.
     If you make a mistake in editing, exit and start again from this step.
     (It is not currently supported to ‘undo’ or go back to previous steps.)

From this point, follow the steps in **one** of the subsections below.

Create an item scheme (Agency Scheme, Code list, or Concept Scheme)
-------------------------------------------------------------------

3. Choose the class to create.

   Type **one of** :kbd:`1`, :kbd:`2`, **or** :kbd:`3`.
   Type :kbd:`Enter`.

4. Enter information about the item scheme.

   Like every ‘maintainable’ SDMX artefact, an item scheme has the following attributes.
   These allow to distinguish the artefact from others, and for a responsible person (you!) to *maintain* it by publishing different versions.

   Type each one as prompted, followed by :kbd:`Enter`.

   - **Maintainer ID.**
     This will be ``TDCI``, or if you are maintaining structures for another organization, the ID (not full name) of that organization.
   - **ID** of the item scheme itself.
     See the :doc:`/standards` for information about what to use here.
   - **Name** of the item scheme.
     This is optional.
   - **Version.**
     ``1.0.0`` is a safe default or initial value.
     If you enter a version that is already in use, the existing stored SDMX artefact will be **overwritten**.
     You may choose to do this deliberately, or choose a different version to avoid this.

   These three pieces together are used to construct the **Uniform Resource Name (URN)** of the item scheme.
   The URN can be used to locate and identify the item scheme later.
   The full URN looks like::

       urn:sdmx:org.sdmx.infomodel.datastructure.Codelist=TDCI:CL_EXAMPLE(1.0.0)

   :mod:`.transport_data` supports using *shortened URNs*, for example ``Codelist=TDCI:CL_EXAMPLE(1.0.0)`` (specific version) or ``Codelist=TDCI:CL_EXAMPLE`` (implicitly the latest version).

5. Add 0 or more items to the scheme, or edit current items.

   A list of the current items in the scheme (if any) is shown.

   Type **either** :kbd:`n` for a new item **or** the number of an existing item; followed by :kbd:`Enter`.

6. Enter information about the new or existing item.

   Items within item schemes are ‘identifiable’ SDMX artefacts.
   These have fewer attributes than ‘maintainable’ artefacts (such as the parent item scheme):

   Type each one as prompted, followed by :kbd:`Enter`.

   - **ID** of the item.
   - **Name** of the item.
     This is optional.

   Type :kbd:`Enter` again to finish the entry of this item.

7. Repeat steps (5) and (6) as many times as needed.
   Then, type :kbd:`Enter` to finish.

8. Save the created item scheme.

   Type :kbd:`y` followed by :kbd:`Enter`.
   The created SDMX artefact is saved to the local store.

   You can confirm this by using :program:`tdc store` command and subcommands to query the store, for example::

       # Show all artefacts with "TDCI" as maintainer
       tdc store list --maintainer=TDCI

       # Show a particular artefact
       tdc store show "Codelist=TDCI:CL_EXAMPLE(1.0.0)"

The program exits.
To create or edit other structures, run :program:`tdc edit` again.

Create a data structure definition (DSD)
----------------------------------------

3. Choose to create a new DSD.

   Type :kbd:`5`, followed by :kbd:`Enter`.

4. Enter information about the DSD.
   This is the same as step (4) in the Item Scheme section, above.

5. Add 1 or more DSD **dimensions**.

   Type the ID of each dimension, followed by :kbd:`Enter`.

   After the last dimension, type :kbd:`Enter` (with no text) to finish the entry of dimensions.

6. Add the DSD **measure**.

   The ‘measure’ is answers the question “What is measured by each observation value?”
   A broader SDMX convention is to use the ID ``OBS_VALUE`` and store elsewhere (in metadata) a reference to a concept (vehicle sales; energy consumption; etc.) that describes the actual measure.

   Type ``OBS_VALUE`` followed by :kbd:`Enter`.

   Type :kbd:`Enter` again to finish the entry of measures. [1]_

7. Add 0 or more DSD **attributes**.

   An attribute stores information *about* observations, other than their *value*.
   For example, information that an observation's value is estimated is stored as an attribute.
   Attributes can be attached to individual observations, to groups of observations, or to entire data sets.
   (:program:`tdc edit` does not yet support specifying these.)

   Some attributes commonly used in SDMX applications include:

   - ``OBS_STATUS``: Observation status (usually for individual observations).
   - ``UNIT_MEASURE``: Units of measurement (usually for entire data sets/flows).
   - ``COMMENT``

   Type the ID of each attribute, followed by :kbd:`Enter`.

   After the last attribute, type :kbd:`Enter` (with no text) to finish the entry of attributes.

8. Save the created DSD.
   This is the same as step (8) in the Item Scheme section, above.

Create a data flow definition (DFD)
-----------------------------------

3. Choose to create a new DFD.

   Type :kbd:`4`, followed by :kbd:`Enter`.

4. Enter information about the DFD.
   This is the same as step (4) in the Item Scheme section, above.

5. Enter the URN for the DSD that gives the structure of data sets in this data flow.

   For example, type ``DataStructureDefinition=TDCI:EXAMPLE(1.0.0)``, followed by :kbd:`Enter`.

   The referenced URN **must** already be present in your local store of SDMX artefacts.

6. Save the created DFD.
   This is the same as step (8) in the Item Scheme section, above.

.. [1] SDMX (from version 3.0.0) supports data structures in which each observation has two or more values for different measure concepts.
   This feature is not widely used, and not yet supported by :mod:`transport_data`.
   Thus, we only enter a single measure.
