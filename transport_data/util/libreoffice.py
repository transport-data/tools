"""Utilities for LibreOffice."""

import logging
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pathlib

log = logging.getLogger(__name__)

#: Expected name of the LibreOffice command-line program.
PROGRAM = "soffice"

try:
    assert (
        subprocess.run([PROGRAM, "--version"], stdout=subprocess.DEVNULL).returncode
        == 0
    )
except Exception:
    #: :any:`True` if :data:`PROGRAM` is present on the system
    HAS_LIBREOFFICE = False
else:
    HAS_LIBREOFFICE = True


def to_pdf(path: "pathlib.Path") -> None:
    """Convert LibreOffice-compatible file at `path` to PDF."""
    if not HAS_LIBREOFFICE:
        log.info(f"{PROGRAM!s} not found; skip conversion of {path}")
        return

    subprocess.check_call(
        [PROGRAM, "--headless", "--convert-to", "pdf", "--outdir"]
        + [str(path.parent), str(path)]
    )
