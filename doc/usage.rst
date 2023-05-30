Usage
*****

Installation
============

`Python <https://www.python.org/downloads/>`__ and `pip <https://docs.python.org/3/installing/index.html>`__ are required.
Install the latest numbered release from PyPI using e.g.::

    $ pip install transport-data[docs,tests]

This will also install dependencies for development and testing.
Or, install from source:

- Clone the repository::

    $ git clone git@github.com:transport-data/tools.git

- In the cloned directory, run::

    $ pip install .[docs,tests]

You will likely also want to:

- Install the `GitHub CLI <https://github.com/cli/cli#installation>`__.
- Clone the `transport-data/registry <https://github.com/transport-data/registry>`__ repository.
  The :program:`tdc` command-line interface provides commands to help with this::

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
