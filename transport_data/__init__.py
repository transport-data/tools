import logging
import sys

from .config import Config

logging.basicConfig(level=logging.INFO, handlers=logging.StreamHandler(sys.stdout))
logging.getLogger(__name__).setLevel(logging.INFO)

CONFIG = Config.read()
