import logging
import sys
from warnings import filterwarnings

from .config import Config
from .store import UnionStore
from .util.pluggy import register_internal

filterwarnings("ignore", "pkg_resources is deprecated", UserWarning, "ckanapi.version")

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))

#: Global configuration.
CONFIG = Config.read()

#: Global access to data storage.
STORE = UnionStore(CONFIG)

# Register plugin hooks
register_internal(
    "ato",
    "iamc",
    "ipcc",
    "iso",
    "itdp",
    "jrc",
    "oica",
    "org",
    "other",
)
