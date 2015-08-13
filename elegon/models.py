# coding: utf-8

import json
import datetime
import sqlalchemy.exc
from sqlalchemy.ext.declarative import declared_attr

from elegon.ext import db
from elegon.utils import random_string, unparse_crontab

class Base(db.Model):

    __abstract__ = True

    @declared_attr
    def id(cls):
        return db.Column('id', db.Integer, primary_key=True, autoincrement=True)

    @classmethod
    def get(cls, id):
        return cls.query.filter(cls.id == id).first()

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(i) for i in ids]

    def to_dict(self):
        keys = [c.key for c in self.__table__.columns]
        return {k: getattr(self, k) for k in keys}

    def __repr__(self):
        attrs = ', '.join('{0}={1}'.format(k, v) for k, v in self.to_dict().iteritems())
        return '{0}({1})'.format(self.__class__.__name__, attrs)

class Crontab(Base):
    """需要执行的定时任务"""

    __tablename__ = 'crontab'

    name = db.Column(db.String(255))
    status = db.Column(db.String(10), default='off')
    _cron = db.Column(db.Text, default='{}')
    _props = db.Column(db.Text, default='{}')
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)

    cronjobs = db.relationship('CronJob', backref='crontab', lazy='dynamic')

    def __init__(self, name, cron, props):
        self.name = name
        self._cron = json.dumps(cron)
        self._props = json.dumps(props)

    @classmethod
    def create(cls, name, cron, props):
        c = cls(name, cron, props)
        db.session.add(c)
        db.session.commit()
        return c

    @classmethod
    def list_all(cls, start=0, limit=20):
        q = cls.query.order_by(cls.id.desc())
        return q.count(), q[start:start+limit]

    @property
    def crontab_kwargs(self):
        return json.loads(self._cron)

    @property
    def schedule_string(self):
        return unparse_crontab(self.crontab_kwargs)

    @property
    def props(self):
        return json.loads(self._props)

    def on(self):
        self.status = 'on'
        db.session.add(self)
        db.session.commit()

    def off(self):
        self.status = 'off'
        db.session.add(self)
        db.session.commit()

    def add_job(self, container_id):
        j = CronJob.create(self.id, container_id)
        if not j:
            return
        self.cronjobs.append(j)
        return j

    def list_jobs(self, start=0, limit=20):
        q = self.cronjobs.order_by(CronJob.id.desc())
        return q.count(), q[start:start+limit]


class CronJob(Base):

    __tablename__ = 'cronjob'
    
    tab_id = db.Column(db.Integer, db.ForeignKey('crontab.id'))
    container_id = db.Column(db.String(64), index=True)
    status = db.Column(db.String(10), default='running')
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    finish_at = db.Column(db.DateTime)

    def __init__(self, tab_id, container_id):
        self.tab_id = tab_id
        self.container_id = container_id

    @classmethod
    def create(cls, tab_id, container_id):
        j = cls(tab_id, container_id)
        db.session.add(j)
        db.session.commit()
        return j

    @classmethod
    def get_by_container_id(cls, cid):
        return cls.query.filter(cls.container_id.like('{}%'.format(cid))).first()

    def set_status(self, status):
        self.status = status
        db.session.add(self)
        db.session.commit()

class User(Base):

    __tablename__ = 'user'

    name = db.Column(db.String(255), index=True, nullable=False, default='')
    email = db.Column(db.String(255), unique=True, nullable=False, default='')
    token = db.Column(db.String(255), unique=True, nullable=False, default='')
    admin = db.Column(db.Boolean, default=False)

    def __init__(self, name, email, token):
        self.name = name
        self.email = email
        self.token = token

    @classmethod
    def get_or_create(cls, name, email):
        u = cls.get_by_email(email)
        if u:
            return u
        try:
            u = cls(name, email, random_string(20))
            db.session.add(u)
            db.session.commit()
            return u
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return None

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter(cls.email == email).first()

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter(cls.name == name).first()

    @classmethod
    def get_by_token(cls, token):
        return cls.query.filter(cls.token == token).first()

    @classmethod
    def list_users(cls, start=0, limit=20):
        return cls.query.offset(start).limit(limit).all()
