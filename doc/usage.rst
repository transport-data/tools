Usage
*****

Installation
============

Install the latest numbered release from PyPI using e.g.::

    $ pip install transport-data

or, install from source:

- Clone the repository::

    $ git clone git@github.com:transport-data/tools.git

- In the cloned directory, run::

    $ pip install .[docs,tests]

  This will also install dependencies for development and testing.

You will likely also want to:

- Install the `GitHub CLI <https://github.com/cli/cli#installation>`__.
- Clone the `transport-data/registry <https://github.com/transport-data/registry>`__ repository::

    $ tdc config set tdc_registry_local /path/for/local/clone
    $ tdc registry clone

Command-line
============

Use the tools via the command-line interface (:mod:`transport_data.cli`).
Each subcommand has its own :program:`--help` and page in this documentation.

From other Python code
======================

.. code-block::

   from transport_data import estat

   f = estat.list_flows()
