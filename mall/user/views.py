# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template,session,redirect,url_for,request,abort,flash
from flask_login import login_required,login_user,current_user
from  sqlalchemy  import desc
from flask_wechatpy import oauth
from mall.extensions import db
import time,random

from mall.user.models import User
from mall.public.models import BuysCar,UserOrder,UserAddress
from mall.store.models import Sale,Goods,Seller
from mall.utils import templated
from .forms import AddUserAddressForm

blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')


@blueprint.route('/')
@templated()
@login_required
def members():
    """List members."""
    return dict()


#显示购物车
@blueprint.route('/my_buys_car')
@templated()
@login_required
def my_buys_car():
	buys_car = BuysCar.query.filter_by(users=current_user).all()
	return dict(buys_car=buys_car)


#显示我的订单
@blueprint.route('/my_order')
@templated()
@login_required
def my_order():
	# user_order = UserOrder.query.filter_by(users_buy=current_user).all()
	user_order = UserOrder.query\
		.with_entities(
			UserOrder.id,UserOrder.number,UserOrder.buy_time,UserOrder.pay_price,UserOrder.order_state,UserOrder.goods_number\
		)\
		.order_by(desc(UserOrder.id))\
		.all()
	return dict(order=user_order)


#显示订单详细
@blueprint.route('/show_my_order/<int:id>')
@templated()
@login_required
def show_my_order(id=0):
	user_order_id = id
	
	user_order = Sale.query\
		.with_entities(Sale,UserOrder,Goods,Seller)\
		.join(UserOrder,UserOrder.id==Sale.UserOrder_id)\
		.join(Goods,Goods.id==Sale.goods_id)\
		.join(Seller,Seller.id==Goods.sellers_id)\
		.filter(UserOrder.id==user_order_id)\
		.all()

	if not user_order:
		abort(404)

	user_order_dict = {}
	for i in user_order:
		if user_order_dict.__contains__(str(i[1].id)):
			user_order_dict[str(i[1].id)].append(i)
		else:
			user_order_dict[str(i[1].id)] = [i]

	#是否非法查看他人信息
	for k,v in user_order_dict.items():
		if v[0][1].users_buy !=current_user:
			abort(404)

	return dict(order=user_order_dict)



#显示我的关注
@blueprint.route('/my_follow')
@templated()
@login_required
def my_follow():
	return dict()


#添加收货地址
@blueprint.route('/add_user_address')
@templated()
@login_required
def add_user_address():
	form = AddUserAddressForm()
	return dict(form=form)

#添加用户地址
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
		flash('添加成功','success')
	else:
		flash('添加失败','danger')
		flash_errors(form)

	return redirect(url_for('public.submit_order'))


#自动注册 
# @blueprint.route('/autoregister')
def autoregister(wechat_id=''):
	
	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	username_str = ''
	password_str = ''
	str_time =  time.time()
	username_str = 'AU'
	username_str += str(int(int(str_time)*1.301))
	for i in range(2):
		username_str += random.choice(choice_str)

	for i in range(6):
		password_str += random.choice(choice_str)

	username = username_str
	password = password_str

	user = []

	if not wechat_id:
		wechat_id = session.get('wechat_user_id','')
		user = User.query.filter_by(wechat_id=wechat_id).first()
	else:
		users = [] 
	if user:
		login_user(user,True)
		return user 
	user = User.query.filter_by(username=username).first()
	if user is None:
		user = User.create(
			username=username,
			password=password,
			wechat_id=wechat_id,
		)
		login_user(user,True)
		return user 
	else:
		autoregister()


@blueprint.route('/autologin/<string:name>')
@blueprint.route('/autologin')
# @oauth(scope='snsapi_base')
def autologin(name=''):
	if name:
		user = User.query.filter_by(username=name).first()
		login_user(user,True) if user else abort(404)
		return redirect(request.args.get('next') or url_for('public.home'))

	wechat_id = session.get('wechat_user_id','')
	if wechat_id:
		user = User.query.filter_by(wechat_id=wechat_id).first()
	else: 
		user = []
	if user :
		login_user(user,True)
	else:
		user = autoregister()

	return redirect(request.args.get('next') or url_for('public.home'))
		
