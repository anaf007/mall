#coding=utf-8
from flask import Blueprint, flash, redirect, render_template, request, url_for,current_app
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from flask_login import current_user,login_required

from mall.extensions import executor
from log import logger
from .models import SystemVersion,Category,BaseProducts
from mall.utils import templated,flash_errors,allowed_file,gen_rnd_filename,send_email
from . import blueprint
from .forms import AddCategoryForm,AddBaseProductForm
from mall.decorators import admin_required
from mall.user.models  import Permission,User

import datetime as dt
import os

@blueprint.route('/')
@templated()
def home():
    
    if not current_user.is_authenticated:
        return redirect(url_for('auth.user_login',next=request.endpoint))
    
    if not current_user.can(Permission.ADMINISTER):
        abort(401)

    # logger.debug('----')
    # logger.info('----')
    # logger.error('----')
    # logger.warning('----')

    executor.submit(send_email,f'id:{current_user.id}已登录后台')
    try:
        send_email(f'id:{current_user.id}已登录后台')
    except Exception as e:
        print(str(e))
    
    return dict()

@blueprint.route('/index')
@templated('superadmin/home.html')
@login_required
@admin_required
def index(): 
    executor.submit(send_email,f'id:{current_user.id}已登录后台')
    try:
        send_email(f'id:{current_user.id}已登录后台')
    except Exception as e:
        print(str(e))
    
    return  dict()


@blueprint.route('/all_version')
@templated()
@login_required
@admin_required
def all_version():
	return dict(version=SystemVersion.query.order_by(desc('id')).all())


@blueprint.route('/add_version',methods=['POST'])
@login_required
@admin_required
def add_version_post():
	SystemVersion.create(
		number=request.form.get('number',' '),
		title=request.form.get('title',' '),
		summary=request.form.get('summary',' '),
		context=request.form.get('context',' '),	
	)
	flash('添加完成.','success')
	return redirect(url_for('.all_version'))


#分类
@blueprint.route('/category')
@templated()
@login_required
@admin_required
def category():
	return dict(categorys=Category.query.order_by('sort').all())


#分类
@blueprint.route('/add_category')
@templated()
@login_required
@admin_required
def add_category():
	return dict(form=AddCategoryForm())


@blueprint.route('/add_category',methods=["POST"])
@login_required
@admin_required
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
			active=True,			
		)
		flash('添加成功','success')
		return redirect(url_for('.add_category'))
	else:
		flash('添加失败','danger')
		flash_errors(form)
	return redirect(url_for('.add_category'))


#商品基础数据
@blueprint.route('/base_products/<int:page>')
@blueprint.route('/base_products')
@templated()
@login_required
@admin_required
def base_products(page=1):
    pagination = BaseProducts.query.order_by(desc('id')).paginate(page,20,error_out=False)
    return dict(pagination=pagination,base_product=pagination.items)


#添加商品基础数据
@blueprint.route('/add_base_product')
@templated()
@login_required
@admin_required
def add_base_product():

	return dict(form=AddBaseProductForm())


@blueprint.route('/add_base_product',methods=['POST'])
@login_required
@admin_required
def add_base_product_post():
    form=AddBaseProductForm()
    if form.validate_on_submit():
        f = request.files['image']
        filename = secure_filename(gen_rnd_filename() + "." + f.filename.split('.')[-1])
        if not filename:
            flash(u'请选择图片','danger')
            return redirect(url_for('.add_base_product'))
        if not allowed_file(f.filename):
            flash(u'图文件名或格式错误。','danger')
            return redirect(url_for('.add_base_product'))

        dataetime = dt.datetime.today().strftime('%Y%m%d')
        file_dir = 'superadmin/%s/base_products/%s/'%(current_user.id,dataetime)
        if not os.path.isdir(os.getcwd()+'/'+current_app.config['UPLOADED_PATH']+file_dir):
            os.makedirs(os.getcwd()+'/'+current_app.config['UPLOADED_PATH']+file_dir)
        f.save(current_app.config['UPLOADED_PATH'] +file_dir+filename)

        BaseProducts.create(
            title=form.title.data,
            original_price=form.original_price.data,
            special_price=form.special_price.data,
            unit=form.unit.data,
            ean=form.ean.data,
            note=form.note.data,
            category_id=form.category_id.data,            
            attach_key=form.attach_key.data,            
            attach_value=form.attach_value.data,
            main_photo = file_dir+filename,        	
        )
        flash('添加成功','success')
    else:
        flash('数据校验失败。','danger')
    return redirect(url_for('superadmin.add_base_product'))


# 删除基础数据
@blueprint.route('/delete_base_product/<int:id>')
@login_required
@admin_required
def delete_base_product(id=0):
    base_product = BaseProducts.query.get_or_404(id)
    base_product.delete()
    flash('删除完成','success')
    return redirect(url_for('.base_products'))


#所有用户
@blueprint.route('/all_users/<int:page>')
@blueprint.route('/all_users')
@templated()
@login_required
@admin_required
def all_users(page=1):
    pagination = User.query.order_by(desc('id')).paginate(page,20,error_out=False)
    return dict(all_users=pagination.items,pagination=pagination)






