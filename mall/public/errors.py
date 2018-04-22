#coding=utf-8

from . import blueprint
from flask import flash,render_template

@blueprint.errorhandler(500)
def internal_server_error(e):
	flash(str(e))
	return render_template('500.html'), 500

@blueprint.errorhandler(404)
def page_not_found(e):
	flash(str(e))
	return render_template('404.html'), 404