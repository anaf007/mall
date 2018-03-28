# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, abort,Response
from flask_login import login_required, login_user, logout_user,current_user
from sqlalchemy import desc

from mall.extensions import login_manager,db
from mall.user.forms import RegisterForm
from mall.user.models import User
from mall.store.models import Seller,Goods,Inventory,GoodsAllocation,Sale
from mall.utils import flash_errors,templated
from .models import Follow,BuysCar,UserAddress,UserOrder


import random,time


blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/')
@templated()
def home():
    """Home page."""
    follow = Follow.query.filter_by(users=current_user).all()
    len_follow = len(follow)
    if len_follow>0 and len_follow<=1:
    	return redirect(url_for('.show_store',id=follow[0].id))
    if len_follow<1:
    	return u'您还未关注店铺。'
    return dict()


#显示店铺
@blueprint.route('/show_store/<int:id>')
@templated()
def show_store(id=0):
    follow = Follow.query.get_or_404(id)
    seller = Seller.query.get_or_404(follow.seller_id)
    goods = seller.goods_id
    return dict(seller=seller,goods=goods)


#添加购物车
@blueprint.route('/add_car/<int:id>')
@templated()
def add_car(id=0):
	goodsed = Goods.query.get_or_404(id)
	is_goods = BuysCar.query.filter_by(users=current_user).filter_by(goodsed=goodsed).first()
	if is_goods:
		count = is_goods.count+1
		is_goods.update(count=count)
	else:
		BuysCar.create(users=current_user,goodsed=goodsed)
	return dict()


#显示商品详情
@blueprint.route('/show_goods/<int:id>')
@templated()
def show_goods(id=0):
	goods = Goods.query.get_or_404(id)
	goods.update(click_count=goods.click_count+1)
	return dict(goods=goods)



@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))



@blueprint.route('/add_user_address',methods=['POST'])
def add_user_address_post():
	form = AddUserAddressForm()
	if form.validate_on_submit():
		user_address = UserAddress()
		user_address.name = form.name.data
		user_address.phone = form.phone.data
		user_address.address = form.address.data
		user_address.users = current_user
		if not UserAddress.query.filter_by(users=current_user).first():
			user_address.state = 0
		db.session.add(user_address)
		db.session.commit()
		flash(u'添加成功','success')
	else:
		flash(u'添加失败','danger')
		flash_errors(form)

	return redirect(url_for('.add_user_address'))


#购物车提交订单
@blueprint.route('/submit_order')
@templated()
def submit_order():
	#购物车信息
	buys_car = BuysCar.query.filter_by(users=current_user).all()
	#收货地址信息：
	user_address = UserAddress.query.filter_by(users=current_user).order_by(desc(UserAddress.state)).all()
	return dict(buys_car=buys_car,user_address=user_address)


#购物车确认下单
@blueprint.route('/confirm_order',methods=['POST'])
def confirm_order():
	"""
	检查是否有不同商家商品
	检查商家是否足够库存
	减去库存
	保存订单	
	减去商家库存数量
	删除购物车
	"""
	user_address = UserAddress.query.get(request.form.get('user_address',0))
	if not user_address:
		flash(u'您未添加收货地址，请填写填写收货地址。')
		abort(401)

	buys_car = BuysCar.query.filter_by(users=current_user).all()

	#检查是否有不同商家商品
	is_has = {}
	seller = ''
	for i in buys_car:
		if not is_has.has_key(str(i.goodsed.sellers_id)):
			if not is_has:
				is_has[str(i.goodsed.sellers_id)] = i
				seller = i.goodsed.sellers_id
			else:
				flash(u'不能提交订单，存在不同商家的商品，请返回购物车重新修改')
				abort(401)			
	#end检查是否有不同商家商品

	#检查商家是否足够库存
	all_goodsed_id = []

	for i in buys_car:
		all_goodsed_id.append(i.goods_id)
	#获取购物车里商品库存数, 根据货位排序扣除库存的
	all_goods = Inventory.query\
		.filter(Inventory.goods_id.in_(all_goodsed_id))\
		.join(GoodsAllocation,GoodsAllocation.id==Inventory.goods_allocation_id)\
		.order_by(GoodsAllocation.sort)\
		.all()
	goodsed_dic = {}
	for i in all_goods:
		if goodsed_dic.has_key(str(i.goods_id)):
			goodsed_dic[str(i.goods_id)].append(i)
		else:
			goodsed_dic[str(i.goods_id)] = [i]	
	for i in buys_car:
		count = i.count
		for j in goodsed_dic[str(i.goods_id)]:
			#库存数减去购物车数量
			if j.count - count >= 0:
				break;
			if j.count - count < 0:
				count = count - j.count
		else:
			abort(Response(u'店家该商品：%s库存不足'%i.goods_id))
	#end检查商家是否足够库存

	#出库单
	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	str_time =  time.time()
	number_str = 'T'
	number_str += str(int(int(str_time)*1.301))
	for i in range(2):
		number_str += random.choice(choice_str)

	#出库单
	user_order = UserOrder()
	user_order.user_id = current_user.id
	user_order.receive = user_address.id
	user_order.number = number_str
	user_order.note = request.form.get('note','')
	user_order.seller_id = all_goods[0].goodsed.sellers_id

	db.session.add(user_order)


	# 减去库存
	for i in buys_car:
		count = i.count
		for j in goodsed_dic[str(i.goods_id)]:

			#销售的商品记录
			sale = Sale()
			sale.seller_id = seller
			sale.goods_id = i.goods_id
			sale.count = i.count
			sale.residue_count = seller
			sale.user_order = user_order
			sale.seller_id = i.goodsed.sellers_id
			#如果库存数量大于购物车数量
			if j.count - count >= 0:
				#出售记录表
				sale.residue_count = j.count - count
				sale.goods_allocation_id = j.goods_allocation_id
				
				#更新库存
				j.count = j.count - count
				db.session.add(j)
				break;

			#如果库存数量少于购物车数量
			if j.count - count < 0:
				sale.residue_count = 0
				sale.goods_allocation_id = j.goods_allocation_id
				count = count - j.count
				
				#删除库存
				db.session.delete(j)

			db.session.add(sale)

	# end减去库存

	# 删除购物车
	for i in buys_car:
		db.session.delete(i)
	#end删除购物车

	try:
		db.session.commit()
		flash(u'订单提交成功')
	except Exception, e:
		db.session.rollback()
		return str(e)

	return redirect(url_for('.submit_order'))





