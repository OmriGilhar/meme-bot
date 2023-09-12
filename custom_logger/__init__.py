import sys
from loguru import logger


logger.remove(0)
logger.add(sys.stderr, format="{time:MMM D, YYY > HH:mm:ss} | {level} | {message}")
