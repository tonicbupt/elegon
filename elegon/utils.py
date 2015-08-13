# coding: utf-8

import random
import string
import inspect
from functools import wraps
from flask import abort, g, redirect

from elegon.ext import openid2

def need_login(f):
    @wraps(f)
    def _(*args, **kwargs):
        if not g.user:
            return redirect(openid2.login_url)
        return f(*args, **kwargs)
    return _

def need_admin(f):
    @wraps(f)
    def _(*args, **kwargs):
        if not g.user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return _

def make_kwargs(f):
    @wraps(f)
    def _(*args, **kwargs):
        ags = inspect.getargspec(f)
        kw = dict(zip(ags.args, args))
        kw.update(kwargs)
        return kw
    return _

def run_with_appcontext(f):
    @wraps(f)
    def _(*args, **kwargs):
        from elegon.app import create_app
        app = create_app()
        with app.app_context():
            return f(*args, **kwargs)
    return _

def paginator_kwargs(kw):
    d = kw.copy()
    d.pop('start', None)
    d.pop('limit', None)
    return d

def random_string(length):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))

crontab_keys = (
    'second',
    'minute',
    'hour',
    'day',
    'week',
    'month',
    'year',
)

def parse_crontab(cron):
    cron = cron.split(' ')
    if len(cron) != 7:
        return
    return dict(zip(crontab_keys, cron))

def unparse_crontab(cron_dict):
    values = [cron_dict[key] for key in crontab_keys]
    return ' '.join(values)
