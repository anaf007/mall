#coding=utf-8
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import desc
from .models import SystemVersion

from . import blueprint

@blueprint.route('/')
def home():
	return render_template('superadmin/home.html')


@blueprint.route('/all_version')
def all_version():
	return render_template('superadmin/all_version.html',version=SystemVersion.query.order_by(desc('id')).all())


@blueprint.route('/add_version',methods=['GET'])
def add_version():
	version = SystemVersion.query.order_by(desc('id')).first()
	return render_template('superadmin/add_version.html',version=version)


@blueprint.route('/add_version',methods=['POST'])
def add_version_post():
	SystemVersion.create(
		number=request.form.get('number',' '),
		title=request.form.get('title',' '),
		summary=request.form.get('summary',' '),
		context=request.form.get('context',' '),	
	)
	flash(u'添加完成.','success')
	return redirect(url_for('.all_version'))


