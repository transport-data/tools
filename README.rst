Tools for the Transport Data Commons
************************************

Usage
=====

- Clone the repository, e.g. ``git clone git@github.com:transport-data/tools.git``.
- In the cloned directory, run ``pip install .`` —this will also install dependencies.
- Use the tools via the command-line interface (CLI)::

    $ tdc --help
    Usage: tdc [OPTIONS] COMMAND [ARGS]...

      Transport Data Commons tools.

    Options:
      --help  Show this message and exit.

    Commands:
      adb       Asian Development Bank (ADB) data provider.
      config    Manipulate configuration.
      estat     Eurostat (ESTAT) data provider.
      org       Information about the TDCI per se.
      proto     TDC prototype debugging.
      registry  Manipulate the registry repo.

  Each subcommand has its own --help.

Development
===========

- Python code:

  - Use `black <https://black.rtfd.io>`__.

- Exchange MaintainableArtefacts between modules.
