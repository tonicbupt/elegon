# coding: utf-8

import json

from flask import Flask, request, g
from werkzeug.utils import import_string

from elegon.ext import db, openid2
from elegon.models import User
from elegon.utils import paginator_kwargs
from elegon.schedule import init_scheduler

blueprints = (
    'index',
    'crontab',
    'ajax',
)

def create_app(init=False):
    app = Flask(__name__, static_url_path='/elegon/static', template_folder='templates')
    app.config.from_object('elegon.config')
    app.secret_key = 'c534d51a57638e8a8a51c36d4a4128b89f8beb22'

    for ext in (db, openid2):
        ext.init_app(app)

    for bp in blueprints:
        import_name = '%s.ui.%s:bp' % (__package__, bp)
        app.register_blueprint(import_string(import_name))

    for fl in (max, min, paginator_kwargs, enumerate):
        app.add_template_global(fl)

    with app.app_context():
        db.create_all()

    @app.before_request
    def init_global_vars():
        user_dict = json.loads(request.cookies.get(app.config['OPENID2_PROFILE_COOKIE_NAME'], '{}'))
        g.user = user_dict and User.get_or_create(user_dict['username'], user_dict['email']) or None
        g.start = request.args.get('start', type=int, default=0)
        g.limit = request.args.get('limit', type=int, default=20)

    if init:
        s = init_scheduler()
        s.start()
    return app
