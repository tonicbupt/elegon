# coding: utf-8

from flask import Blueprint, url_for, redirect

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    return redirect(url_for('crontab.list_crons'))
