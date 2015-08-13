# coding: utf-8

from flask import url_for
from eruhttp import EruException
from apscheduler.schedulers.background import BackgroundScheduler

from elegon.config import SQLALCHEMY_DATABASE_URI, DEBUG
from elegon.ext import eru
from elegon.models import Crontab
from elegon.utils import run_with_appcontext

scheduler = None

def init_scheduler():
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore('sqlalchemy', url=SQLALCHEMY_DATABASE_URI)
    return scheduler

def add_crontab(crontab):
    scheduler.add_job(run_crontab, 'cron', id=str(crontab.id), args=(crontab.id,), **crontab.crontab_kwargs)
    crontab.on()

def remove_crontab(crontab):
    scheduler.remove_job(str(crontab.id))
    crontab.off()

def get_crontab(crontab):
    return scheduler.get_job(str(crontab.id))

@run_with_appcontext
def run_crontab(crontab_id):
    print 'run crontab'
    crontab = Crontab.get(crontab_id)
    if not crontab:
        return

    # debug 打开并不真正执行任务.
    if DEBUG:
        print '<Crontab %s> started.' % crontab_id
        return

    props = crontab.props
    try:
        r = eru.deploy_private(
            props.get('group', ''),
            props.get('pod', ''),
            props.get('appname', ''),
            1,
            1,
            props.get('version', ''),
            props.get('entrypoint', ''),
            props.get('env', ''),
            props.get('network_ids', []),
            callback_url=url_for('crontab.callback',
                crontab_id=crontab.id, _external=True),
        )
    except EruException as e:
        print e
        return

    task_id = r['tasks'][0]
    while True:
        try:
            task = eru.get_task(task_id)
            if not task['finished']:
                continue
            print task
            crontab.add_job(task['props']['container_ids'][0])
            break
        except EruException as e:
            break
