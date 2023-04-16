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
      config  Manipulate configuration.
      org     Information about the TDCI per se.
      proto   TDC prototype.

  Each subcommand has its own --help.

Development
===========

- Python code:

  - Use `black <https://black.rtfd.io>`.

- Exchange MaintainableArtefacts between modules.
