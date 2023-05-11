Tools for the Transport Data Commons
************************************

.. image:: https://github.com/transport-data/tools/actions/workflows/pytest.yaml/badge.svg
   :target: https://github.com/transport-data/tools/actions/workflows/pytest.yaml
   :alt: "pytest" workflow status badge
.. image:: https://codecov.io/gh/transport-data/tools/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/transport-data/tools
   :alt: Codecov.io test coverage status badge

Installation
============

Install from PyPI using e.g.: ``pip install transport-data``

You will likely also want to:

- Install the `GitHub CLI <https://github.com/cli/cli#installation>`__.
- Clone the `transport-data/registry <https://github.com/transport-data/registry>`__ repository::

    $ tdc config set tdc_registry_local /path/for/local/clone
    $ tdc registry clone

Usage
=====

Use the tools via the command-line interface (CLI)::

    $ tdc --help
    Usage: tdc [OPTIONS] COMMAND [ARGS]...

      Transport Data Commons tools.

    Options:
      --help  Show this message and exit.

    Commands:
      adb       Asian Development Bank (ADB) provider.
      config    Manipulate configuration.
      estat     Eurostat (ESTAT) provider.
      iamc      Demonstrate IAMC structure generation.
      jrc       EU Joint Research Center (JRC) provider.
      org       Information about the TDCI per se.
      proto     TDC prototype debugging.
      registry  Manipulate the registry repo.

Each subcommand has its own --help.

Prototype data
--------------

Use::

    $ tdc adb fetch --all --go
    $ tdc adb convert TAS
    $ tdc jrc fetch --all --go
    $ tdc jrc convert --all

Development
===========

- Install from source:

  - Clone the repository, e.g. ``git clone git@github.com:transport-data/tools.git``.
  - In the cloned directory, run ``pip install .[tests]`` —this will also install dependencies for development and testing.

- Use `Pytest <https://docs.pytest.org>`__: ``pytest``
- Code style and practices:

  - Version as ``vYY.M.D`` using the current date.
  - Use `black <https://black.rtfd.io>`__.
  - Exchange MaintainableArtefacts between modules.
