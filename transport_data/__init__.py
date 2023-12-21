import logging
import sys

from .config import Config
from .registry import Registry

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))

CONFIG = Config.read()
STORE = Registry(CONFIG)
