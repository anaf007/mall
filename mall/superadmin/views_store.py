#coding=utf-8
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import desc
from flask_login import login_required,current_user

from . import blueprint
from mall.utils import templated
from ..store.models import Seller
from mall.decorators import admin_required

@blueprint.route('/store/<int:page>')
@blueprint.route('/store')
@templated('superadmin/store/home.html')
@login_required
@admin_required
def store_home(page=1):
	pagination = Seller.query.order_by(desc('id')).paginate(page,20,error_out=False)
	return dict(pagination=pagination,all_seller=pagination.items)


@blueprint.route('/change_store_enable/<int:id>')
@login_required
@admin_required
def change_store_enable(id=0):
	seller = Seller.query.get_or_404(id)
	seller.update(enable=True)
	flash('店铺"%s"已启用。'%seller.name,'success')
	return redirect(url_for('superadmin.store_home'))





