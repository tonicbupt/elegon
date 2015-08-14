# coding: utf-8

import time
from flask import url_for
from eruhttp import EruException
from apscheduler.schedulers.background import BackgroundScheduler

from elegon.config import SQLALCHEMY_DATABASE_URI, CRONTAB_DEBUG
from elegon.ext import eru
from elegon.models import Crontab, CronJob
from elegon.utils import run_with_appcontext

_scheduler = None

def init_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
        _scheduler.add_jobstore('sqlalchemy', url=SQLALCHEMY_DATABASE_URI)
    return _scheduler

def start_scheduler():
    _scheduler.start()

def stop_scheduler():
    _scheduler.stop()

def add_crontab(crontab):
    _scheduler.add_job(run_crontab, 'cron', id=str(crontab.id), args=(crontab.id,), **crontab.crontab_kwargs)
    crontab.on()

def remove_crontab(crontab):
    _scheduler.remove_job(str(crontab.id))
    crontab.off()

def get_crontab(crontab):
    return _scheduler.get_job(str(crontab.id))

@run_with_appcontext
def run_crontab(crontab_id):
    crontab = Crontab.get(crontab_id)
    if not crontab:
        return

    # debug 打开并不真正执行任务.
    if CRONTAB_DEBUG:
        return

    props = crontab.props
    callback_url = url_for('crontab.callback', crontab_id=crontab.id, _external=True)
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
            callback_url=callback_url,
        )
    except EruException as e:
        print e
        return

    task_id = r['tasks'][0]
    while True:
        time.sleep(1)
        try:
            task = eru.get_task(task_id)
            if not task['finished']:
                continue
            container_id = task['props']['container_ids'][0]

            cronjob = CronJob.get_by_container_id(container_id)
            if not cronjob:
                crontab.add_job(container_id)
                break
        except EruException as e:
            print e
            break
