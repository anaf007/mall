#coding=utf-8

from . import blueprint
from flask import flash,render_template
from mall.utils import send_email
from log import logger
from mall.extensions import executor

@blueprint.errorhandler(500)
def internal_server_error(e):
    logger.error(e)
    executor.submit(send_email,f'500错误{e}')
    return render_template('500.html'), 500

@blueprint.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404