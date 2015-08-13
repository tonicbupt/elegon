# coding:utf-8

from eruhttp import EruException
from flask import Blueprint, jsonify, g
from flask import render_template as rt

from elegon.ext import eru
from elegon.schedule import get_crontab, add_crontab, remove_crontab
from elegon.models import Crontab

bp = Blueprint('ajax', __name__, url_prefix='/j')


@bp.route('/app/<string:appname>/', methods=['GET'])
def get_app(appname):
    try:
        data = eru.list_app_versions(appname, g.start, g.limit)
    except EruException:
        data = {}

    versions = data.get('versions', [])
    html = rt('/components/version_option.html', versions=versions)
    return jsonify({'html': html})

@bp.route('/app/<string:appname>/version/<string:version>/', methods=['GET'])
def get_version(appname, version):
    try:
        v = eru.get_version(appname, version)
        env_data = eru.list_app_env_names(appname)
        entrypoints = v['appconfig']['entrypoints']
    except EruException:
        env_data = {}
        entrypoints = {}

    envs = env_data.get('data', [])
    env_html = rt('/components/env_option.html', envs=envs)
    entrypoint_html = rt('/components/entrypoint_option.html', entrypoints=entrypoints)
    return jsonify({'env': env_html, 'entrypoint': entrypoint_html})

@bp.route('/group/<string:group>/pods/', methods=['GET'])
def list_group_pod(group):
    try:
        pods = eru.list_group_pods(group, g.start, g.limit)
    except EruException:
        pods = []
    pod_html = rt('/components/pod_option.html', pods=pods)
    return jsonify({'pod': pod_html})

@bp.route('/crontab/<int:crontab_id>/on/', methods=['POST'])
def on(crontab_id):
    crontab = Crontab.get(crontab_id)
    if not crontab:
        return jsonify({'r': 1, 'msg': 'not found'})
        
    if get_crontab(crontab):
        return jsonify({'r': 1, 'msg': 'already on'})

    add_crontab(crontab)
    return jsonify({'r': 0, 'msg': 'ok'})

@bp.route('/crontab/<int:crontab_id>/off/', methods=['POST'])
def off(crontab_id):
    crontab = Crontab.get(crontab_id)
    if not crontab:
        return jsonify({'r': 1, 'msg': 'not found'})
        
    if not get_crontab(crontab):
        return jsonify({'r': 1, 'msg': 'already off'})

    remove_crontab(crontab)
    return jsonify({'r': 0, 'msg': 'ok'})
