import logging

from elegon.config import DEBUG

FORMAT = '[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s] %(message)s'

def init_logging():
    level = logging.DEBUG if DEBUG else logging.INFO
    logging.basicConfig(level=level, format='%(message)s')
