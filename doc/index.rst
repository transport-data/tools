.. module:: transport_data

Transport Data Commons tools
****************************

.. toctree::
   :maxdepth: 2
   :caption: Contents:

The Python package `transport-data <https://pypi.org/project/transport-data/>`__ is available from PyPI::

   $ pip install transport-data

It provides tools for working with **Transport Data Commons** (TDC) data and metadata/structures, and is built and maintained by the Transport Data Commons Initiative (TDCI) and members of the broader TDC community.
For more about the TDC, TDCI, and community, see https://transport-data.org.

This documentation is automatically generated from the code available at https://github.com/transport-data/tools.
For more on the design, status, and plans for this package, see :doc:`dev`.

.. toctree::
   :hidden:
   :caption: General

   usage
   dev
   standards
   howto/index
   roadmap
   whatsnew

General
=======

- :doc:`usage`
- :doc:`dev`
- :doc:`standards`
- :doc:`howto/index`
- :doc:`roadmap`
- :doc:`whatsnew`

.. currentmodule:: transport_data

Data and metadata
=================

The following modules contain code tailored to *individual data providers*.
They handle tasks including:

- Parse (meta)data or structure information from providers' idiosyncratic data formats.
- Provide metadata and structure information that is implicit; not directly available from the provider itself.

.. toctree::
   :caption: Data and metadata
   :hidden:

   adb
   estat
   giz
   iamc
   ipcc
   jrc
   oica
   org
   proto

- :mod:`.adb`: :doc:`adb`
- :mod:`.estat`: :doc:`estat`
- :doc:`giz`
- :mod:`.iamc`: :doc:`iamc`
- :mod:`.ipcc`: :doc:`ipcc`
- :mod:`.jrc`: :doc:`jrc`
- :mod:`.oica`: :doc:`oica`
- :mod:`.org`: :doc:`org`
- :mod:`.proto`: :doc:`proto`

Common code and utilities
=========================

The following modules contain *generic* code and utilities usable with (meta)data from multiple providers or sources or created by TDCI.

.. toctree::
   :caption: Common code and utilities
   :hidden:

   cli
   config
   report
   store
   testing
   tests
   util

- :mod:`~transport_data.cli`: :doc:`cli`
- :mod:`.config`: :doc:`config`
- :mod:`.report`: :doc:`report`
- :mod:`.store`: :doc:`store`
- :mod:`.testing`: :doc:`testing`
- :mod:`.tests`: :doc:`tests`
- :mod:`.util`: :doc:`util`

There are also the following top-level objects:

.. autodata:: transport_data.CONFIG
.. autodata:: transport_data.STORE

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
