# coding: utf-8

import os

from flask.ext.sqlalchemy import SQLAlchemy
from eruhttp import EruClient
from .openid2_ext import OpenID2

from elegon.config import ERU_URL

db = SQLAlchemy()
openid2 = OpenID2(file_store_path=os.getenv('ERU_PERMDIR', ''))
eru = EruClient(ERU_URL)

__all__ = ['db', 'openid2', 'eru']
