#coding=utf-8
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import desc
from flask_login import login_required,current_user

from . import blueprint
from mall.utils import templated
from ..store.models import Seller

@blueprint.route('/store')
@templated('superadmin/store/home.html')
@login_required
def store_home():
	all_seller = Seller.query.order_by(desc('id')).all()
	return dict(all_seller=all_seller)


@blueprint.route('/change_store_enable/<int:id>')
@login_required
def change_store_enable(id=0):
	seller = Seller.query.get_or_404(id)
	seller.update(enable=True)
	flash('店铺"%s"已启用。'%seller.name)
	return redirect(url_for('superadmin.store_home'))
