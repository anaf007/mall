#coding=utf-8
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app, abort
from sqlalchemy import desc
from mall.utils import templated, flash_errors
from flask_login import login_required,current_user

from .forms import CreateStoreForm
from .models import Seller

blueprint = Blueprint('store', __name__, url_prefix='/store')


@blueprint.route('/')
@templated('store/home.html')
@login_required
def home():
	# current_app.logger.info("store_info")
	store=current_user.seller_id[0]
	if not store.enable:
		flash(u'您的店铺未启用，请确认管理员是否启用您的店铺。')
		abort(401)
	return dict(store=store)


#店铺申请
@blueprint.route('/create_store')
@templated('store/create_store.html')
@login_required
def create_store():
    return dict(form=CreateStoreForm())


@blueprint.route('/create_store',methods=['POST'])
@templated('store/create_store.html')
@login_required
def create_store_post():
	form = CreateStoreForm()
	if form.validate_on_submit():
		Seller.create(
			users=current_user,
			name = form.name.data,
			address = form.address.data,
			note = form.note.data,
			contact = form.contact.data,
		)
		flash(u'创建成功，等待管理员审核','success')
		return redirect(url_for('.home'))
	else:
		flash_errors(form,)
	return dict(form=form)


#商品管理
@blueprint.route('/commodity_management')
@templated('store/commodity_management.html')
@login_required
def commodity_management():
    return dict(form=CreateStoreForm())






