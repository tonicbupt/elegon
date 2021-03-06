# coding: utf-8

import os

SQLALCHEMY_POOL_SIZE = int(os.getenv('SQLALCHEMY_POOL_SIZE', '100'))
SQLALCHEMY_POOL_TIMEOUT = int(os.getenv('SQLALCHEMY_POOL_TIMEOUT', '10'))
SQLALCHEMY_POOL_RECYCLE = int(os.getenv('SQLALCHEMY_POOL_RECYCLE', '2000'))

MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_USER = os.getenv('MYSQL_USER', 'elegon')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'elegon')

ERU_URL = os.getenv('ERU_URL', 'http://127.0.0.1:5000')

OPENID2_YADIS = 'http://openids.intra.hunantv.com/server/yadis/'
OPENID2_LOGOUT = 'http://openids.intra.hunantv.com/auth/logout/'


DEBUG = bool(int(os.getenv('DEBUG', '1')))
CRONTAB_DEBUG = bool(int(os.getenv('CRONTAB_DEBUG', '0')))
SERVER_NAME = os.getenv('SERVER_NAME', 'localhost:5000')

try:
    from .local_config import *
except ImportError:
    pass

SQLALCHEMY_DATABASE_URI = 'mysql://{0}:{1}@{2}:{3}/{4}'.format(
    MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE,
)
