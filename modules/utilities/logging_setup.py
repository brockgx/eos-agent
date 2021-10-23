import logging
from os import path
from platform import system

UTILITIES_DIR = path.abspath(path.dirname(__file__))
if system() == "Windows":
  LOG_FILE = UTILITIES_DIR + "\\agent.log"
else:
  LOG_FILE = UTILITIES_DIR + "/agent.log"

FORMATTER    = logging.Formatter('[%(asctime)s] (%(filename)s|%(funcName)s|ln %(lineno)d) [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
FORMATTER_BASIC = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
STREAM_HANDLER = logging.StreamHandler()
FILE_HANDLER = logging.FileHandler(LOG_FILE)
LOG_LEVEL = logging.DEBUG

FILE_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setFormatter(FORMATTER_BASIC)

agent_logger = logging.getLogger(__name__)
agent_logger.setLevel(LOG_LEVEL)
agent_logger.addHandler(FILE_HANDLER)
agent_logger.addHandler(STREAM_HANDLER)