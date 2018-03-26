#coding=utf-8
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import desc

from .models import SystemVersion,Category
from mall.utils import templated,flash_errors
from . import blueprint
from .forms import AddCategoryForm

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


#分类
@blueprint.route('/category')
@templated('superadmin/category.html')
def category():
	return dict(categorys=Category.query.order_by('sort').all())

#分类
@blueprint.route('/add_category')
@templated('superadmin/add_category.html')
def add_category():
	return dict(form=AddCategoryForm())


@blueprint.route('/add_category',methods=["POST"])
@templated('superadmin/add_category.html')
def add_category_post():
	form=AddCategoryForm(request.form)
	if form.validate_on_submit():
		if form.pid.data==-1:
			form.pid.data=None
			
		Category.create(
			name=form.name.data,
			ico=form.ico.data,
			sort=form.sort.data,
			parent_id=form.pid.data,
			active=form.active.data,			
		)
		flash(u'添加成功','success')
		return redirect(url_for('.add_category'))
	else:
		flash(u'添加失败','danger')
		flash_errors(form)
	return redirect(url_for('.add_category'))




