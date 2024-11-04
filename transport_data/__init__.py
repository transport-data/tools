import logging
import sys

from .config import Config
from .store import UnionStore
from .util.pluggy import register_internal

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))

#: Global configuration.
CONFIG = Config.read()

#: Global access to data storage.
STORE = UnionStore(CONFIG)

# Register plugin hooks
register_internal(
    "adb",
    "iamc",
    "ipcc.structure",
    "itdp",
    "jrc",
    "oica",
    "org",
)
