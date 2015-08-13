# coding: utf-8

from eruhttp import EruException
from flask import Blueprint, request, abort, g, url_for, redirect, flash
from flask import render_template as rt

from elegon.ext import eru
from elegon.utils import parse_crontab, unparse_crontab
from elegon.models import Crontab, CronJob

bp = Blueprint('crontab', __name__, url_prefix='/crontab')

property_keys = [
    'appname',
    'group',
    'pod',
    'version',
    'entrypoint',
    'env',
    'network_ids',
]

def _get_crontab(crontab_id):
    c = Crontab.get(crontab_id)
    if not c:
        abort(404)
    return c

@bp.route('/list/', methods=['GET'])
def list_crons():
    total, crontabs = Crontab.list_all(g.start, g.limit)
    return rt('/list.html', crontabs=crontabs,
            total=total, endpoint='crontab.list_crons')

@bp.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        try:
            networks = eru.list_network(g.start, g.limit)
            groups = eru.list_groups(g.start, g.limit)
            group = groups and groups[0] and groups[0]['name'] or None
            pods = group and eru.list_group_pods(group) or []
        except EruException:
            groups = []
            networks = []
            pods = []
        return rt('/create.html', groups=groups, networks=networks, pods=pods)

    name = request.form.get('name', '')
    if not name:
        flash(u'给cron取个名字吧', 'error')
        return redirect(url_for('crontab.create'))

    crontab_kwargs = parse_crontab(request.form.get('cron', ''))
    if not crontab_kwargs:
        flash(u'cron 参数不对', 'error')
        return redirect(url_for('crontab.create'))

    props = {key: request.form.get(key, '') for key in property_keys}
    kw = props.copy()
    kw.pop('network_ids', None)
    if not all(kw.values()):
        flash(u'输入参数不对', 'error')
        return redirect(url_for('crontab.create'))

    c = Crontab.create(name, crontab_kwargs, props)
    if not c:
        flash(u'创建出错', 'error')
        return redirect(url_for('crontab.create'))

    return redirect(url_for('crontab.crontab', crontab_id=c.id))

@bp.route('/<int:crontab_id>/', methods=['GET'])
def crontab(crontab_id):
    crontab = _get_crontab(crontab_id)
    cronstring = unparse_crontab(crontab.crontab_kwargs)
    return rt('/crontab.html', crontab=crontab, cronstring=cronstring)

@bp.route('/<int:crontab_id>/history/', methods=['GET'])
def history(crontab_id):
    crontab = _get_crontab(crontab_id)
    total, cronjobs = crontab.list_jobs(g.start, g.limit)
    return rt('/history.html', crontab=crontab, cronjobs=cronjobs,
            total=total, endpoint='crontab.history')

@bp.route('/callback/', methods=['POST'])
def callback():
    data = request.get_json()
    status = data.get('status', '')
    container_id = data.get('container_id', '')
    if not container_id:
        return ''

    cronjob = CronJob.get_by_container_id(container_id)
    if not cronjob:
        return ''

    if status == 'die':
        cronjob.set_status('finished')
    elif status == 'start':
        cronjob.set_status('running')

    eru.remove_containers([container_id, ])
    return ''
