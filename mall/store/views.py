#coding=utf-8
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app, abort
from sqlalchemy import desc
from mall.utils import templated, flash_errors
from flask_login import login_required,current_user

from .forms import *
from .models import Seller,Goods,GoodsAllocation
from mall.user.models import User

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
    return dict(goodsed=Goods.query.filter_by(seller=current_user.seller_id[0]).all())


#商品数据
@blueprint.route('/commodity_data')
@templated('store/commodity_data.html')
@login_required
def commodity_data():
    return dict(form=CommodityDataForm())

#商品数据
@blueprint.route('/commodity_data',methods=['POST'])
@login_required
def commodity_data_post():
	form = CommodityDataForm()
	if form.validate_on_submit():
		Goods.create(
			title=form.title.data,
			original_price=form.original_price.data,
			special_price=form.special_price.data,
			note = form.note.data,
			is_sell = form.is_sell.data,
			hot = form.hot.data,
			ean = form.ean.data,
			unit = form.unit.data,
			seller = current_user.seller_id[0],
			category_id = form.category.data
		)
		flash(u'添加成功','success')
		return redirect(url_for('.commodity_data'))
	else:
		flash(u'添加失败','danger')
		flash_errors(form)
	return redirect(url_for('.commodity_data'))





    



#商品管理
@blueprint.route('/location_management')
@templated('store/location_management.html')
@login_required
def location_management():
    return dict()


#添加仓库
@blueprint.route('/add_warehouse')
@templated('store/add_warehouse.html')
@login_required
def add_warehouse():
    return dict(form=AddWarehouseForm())


#添加仓库
@blueprint.route('/add_warehouse',methods=['POST'])
@login_required
def add_warehouse_post():
	form = AddWarehouseForm()
	state = form.state.data
	max_warehouse = current_user.seller_id[0].max_warehouse
	if max_warehouse<=1:
		if state!=0:
			flash(u'您只允许开通“正常仓”。请重新选择。')
			return redirect(url_for('.add_warehouse'))
	if max_warehouse<=2:
		if state==2 :
			flash(u'您只允许开通“正常仓”和“库存仓”。请重新选择。')
			return redirect(url_for('.add_warehouse'))
	if Warehouse.query.filter_by(seller=current_user.seller_id[0]).count()>=max_warehouse:
		flash(u'您账号最大允许添加:%s个仓库，目前已经有了这么多个不能再添加了。'%str(max_warehouse))
		return redirect(url_for('.add_warehouse'))


	if form.validate_on_submit():
		Warehouse.create(
			name=form.name.data,
			nickname=form.nickname.data,
			seller = current_user.seller_id[0],
			state = state,
		)
		flash(u'添加成功','success')
		return redirect(url_for('.location_management'))
	else:
		flash(u'添加失败','danger')
		flash_errors(form)
	return redirect(url_for('.location_management'))



#添加货位
@blueprint.route('/add_location')
@templated('store/add_location.html')
@login_required
def add_location():
    return dict(form=AddLocationForm())




@blueprint.route('/add_location',methods=['POST'])
@login_required
def add_location_post():
	form = AddLocationForm()
	max_goods_location = current_user.seller_id[0].max_goods_location
	goodsed_allocation_count = GoodsAllocation.query \
		.join(Warehouse,Warehouse.id==GoodsAllocation.warehouse_id) \
		.join(Seller,Seller.id==Warehouse.sellers_id) \
		.join(User,User.id==Seller.user_id) \
		.filter(User==current_user) \
		.count() 

	if GoodsAllocation.query.filter_by(warehouse=current_user.seller_id[0]).count()>=max_goods_location:
		flash(u'您账号最大允许添加:%s个货位，目前已经有了这么多个不能再添加了。'%str(max_goods_location))
		return redirect(url_for('.add_location'))


	if form.validate_on_submit():
		GoodsAllocation.create(
			name = form.name.data,
			sort = form.sort.data,
			note = form.note.data,
			warehouse_id = form.warehouse.data,
		)
		flash(u'添加成功','success')
		return redirect(url_for('.add_location'))
	else:
		flash(u'添加失败','danger')
		flash_errors(form)
	return redirect(url_for('.add_location'))






