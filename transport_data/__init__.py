import logging
import sys

from .config import Config
from .store import UnionStore

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))

CONFIG = Config.read()
STORE = UnionStore(CONFIG)
