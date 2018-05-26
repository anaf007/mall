"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, \
	url_for, abort,Response, jsonify,send_from_directory,current_app
from flask_login import login_required, login_user, logout_user,current_user
from sqlalchemy import desc

from collections import OrderedDict


from mall.extensions import login_manager,db,executor
from mall.user.forms import RegisterForm
from mall.user.models import User
from mall.superadmin.models import Category
from mall.store.models import Seller,Goods,Inventory,GoodsAllocation,Sale
from mall.utils import flash_errors,templated
from .models import Follow,BuysCar,UserAddress,UserOrder
from ..extensions import wechat
from . import blueprint
from .fck import back_submit_order

import random,time,os,sys




@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/')
@templated()
@login_required
def home():
    """Home page."""

    follow = Follow.query.filter_by(users=current_user).all()
    len_follow = len(follow)
    if len_follow == 1:
    	return redirect(url_for('.show_store',seller_id=follow[0].seller_id))
    # if len_follow<1:
    # 	flash('您还未关注店铺。')
    return dict(follow=follow)


#显示店铺
@blueprint.route('/show_store/<int:seller_id>')
@templated()
@login_required
def show_store(seller_id=0):

    #显示主页商品
    goodsed = Goods.query\
        .with_entities(Goods,Category,Seller)\
        .join(Category,Goods.category_id==Category.id)\
        .join(Seller,Seller.id==Goods.sellers_id)\
        .filter(Seller.id==seller_id)\
        .order_by(Category.sort)\
        .all()

    goodsed_dic = {}
    seller_name =  goodsed[0][2].name
    seller_phone=  goodsed[0][2].contact
    seller_id=  goodsed[0][2].id

    #排序  按照商品类别排序
    for i in goodsed:
        value_list = [i]
        if goodsed_dic.__contains__(str(i[1].sort)+'_'+str(i[0].category_id)):
            goodsed_dic[str(i[1].sort)+'_'+str(i[0].category_id)].append(value_list)
        else:
            goodsed_dic[str(i[1].sort)+'_'+str(i[0].category_id)] = [value_list]
    
    #字典排序
    goodseds = [(k,goodsed_dic[k]) for k in sorted(goodsed_dic.keys())]

    goodseds.sort()

    #end显示主页商品

    #购物车
    buys_car = BuysCar.query\
    	.with_entities(BuysCar,Goods)\
    	.join(Goods,Goods.id==BuysCar.goods_id)\
    	.join(User,User.id==BuysCar.user_id)\
    	.filter(User.id==current_user.id)\
    	.all()

    return dict(seller=[seller_name,seller_phone,seller_id],goods=goodseds,buys_car=buys_car)


#添加购物车    $ajax
@blueprint.route('/add_car/')
@blueprint.route('/add_car/<int:id>')
def add_car(id=0):
	goods_id = request.args.get('id','0')

	is_goods = BuysCar.query\
		.with_entities(BuysCar.id,BuysCar.count,Goods.id,Goods.title,Goods.original_price)\
		.join(Goods,Goods.id==BuysCar.goods_id)\
		.filter(BuysCar.users==current_user)\
		.filter(Goods.id==goods_id)\
		.first()

	if is_goods:
		count = is_goods[1]+1
		BuysCar.query.get(is_goods[0]).update(count=count)
		return jsonify({'title':is_goods[3],'price':str(is_goods[4])})

	else:
		BuysCar.create(users=current_user,goods_id=goods_id)
		return jsonify({'title':'该商品','price':0})


#购物城减少
@blueprint.route('/sub_car/')
@blueprint.route('/sub_car/<int:id>')
def sub_car(id=0):
	goods_id = request.args.get('id','0')

	is_goods = BuysCar.query\
		.with_entities(BuysCar.id,BuysCar.count,Goods.id,Goods.title,Goods.original_price)\
		.join(Goods,Goods.id==BuysCar.goods_id)\
		.filter(BuysCar.users==current_user)\
		.filter(Goods.id==goods_id)\
		.first()

	if is_goods:
		count = is_goods[1]-1
		BuysCar.query.get(is_goods[0]).update(count=count)
		return jsonify({'title':is_goods[3],'price':str(is_goods[4])})
	return jsonify({'title':'','price':''})


#删除购物车
@blueprint.route('/delete_car/')
@blueprint.route('/delete_car/<int:id>')
def delete_car(id=0):
	goods_id = request.args.get('id','0')

	is_goods = BuysCar.query\
		.join(Goods,Goods.id==BuysCar.goods_id)\
		.filter(BuysCar.users==current_user)\
		.filter(Goods.id==goods_id)\
		.first()

	if is_goods:
		is_goods.delete()
	return jsonify({'title':'','price':''})




#显示商品详情
@blueprint.route('/show_goods/<int:id>')
@templated()
def show_goods(id=0):
	goods = Goods.query.get_or_404(id)
	goods.update(click_count=goods.click_count+1)
	return dict(goods=goods)


#购物车提交订单
@blueprint.route('/submit_order')
@templated()
@login_required
def submit_order():
	#购物车信息
	# buys_car = BuysCar.query.filter_by(users=current_user).all()
	buys_car = BuysCar.query\
		.with_entities(\
			BuysCar.id,BuysCar.count,\
			Goods.id,Goods.title,Goods.original_price,\
			Seller.freight,Seller.max_price_no_freight,Goods.main_photo,Seller.name,Seller.contact,Seller.note)\
		.join(Goods,Goods.id==BuysCar.goods_id)\
		.join(Seller,Seller.id==Goods.sellers_id)\
		.filter(BuysCar.users==current_user)\
		.all()

	# print(buys_car[0][10])

	#如果购物车为空
	if not buys_car:
		flash('购物车中无货，不能提交订单。')
		abort(401)

	#收货地址信息：
	user_address = UserAddress.query.filter_by(users=current_user).filter_by(state=1).first()
	
	count_price = 0
	for i in buys_car:
		count_price = count_price+i[1]*i[4]

	return dict(buys_car=buys_car,user_address=user_address,count_price=count_price)


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

	user_address = request.form.get('user_address',0)
	user_address = UserAddress.query.get(user_address)
	if not user_address:
		flash('您未添加收货地址，请填写填写收货地址。')
		abort(401)

	buys_car = BuysCar.query\
		.with_entities(
			BuysCar.id,BuysCar.count,BuysCar.goods_id,\
			Goods.title,Goods.original_price,Goods.sellers_id,\
			Seller.name,Seller.freight,Seller.max_price_no_freight,\
			Goods.main_photo,Goods.special_price\
		)\
		.join(Goods,Goods.id==BuysCar.goods_id)\
		.join(Seller,Seller.id==Goods.sellers_id)\
		.filter(BuysCar.users==current_user)\
		.all()
	if not buys_car:
		flash('您的购物车没有东西')
		abort(401)


	#检查是否有不同商家商品
	is_has = {}
	seller = ''
	for i in buys_car:
		if not is_has.__contains__(str(i[5])):
			if not is_has:
				is_has[str(i[5])] = i
				seller = i[5]
			else:
				flash('不能提交订单，存在不同商家的商品，请返回购物车重新修改')
				abort(401)			
	#end检查是否有不同商家商品


	#检查商家是否足够库存
	all_goodsed_id = []

	for i in buys_car:
		all_goodsed_id.append(i[2])
	
	#获取购物车里商品库存数, 根据货位排序扣除库存的
	all_goods = Inventory.query\
		.with_entities(Inventory,GoodsAllocation)\
		.filter(Inventory.goods_id.in_(all_goodsed_id))\
		.join(GoodsAllocation,GoodsAllocation.id==Inventory.goods_allocation_id)\
		.order_by(GoodsAllocation.sort)\
		.all()

	goodsed_dic = {}
	for i in all_goods:
		if goodsed_dic.__contains__(str(i[0].goods_id)):
			goodsed_dic[str(i[0].goods_id)].append(i)
		else:
			goodsed_dic[str(i[0].goods_id)] = [i]	
	
	
	for i in buys_car:
		count = i.count
		try:
			for j in goodsed_dic[str(i[2])]:
				#库存数减去购物车数量
				if j[0].count - count >= 0:
					break;
				if j[0].count - count < 0:
					count = count - j[0].count
			else:
				abort(Response('店家该商品 "%s" 库存不足'%i[3]))

		except Exception as e :
			abort(Response('店家该商品 "%s  "库存不足'%i[3]))
			
	#end检查商家是否足够库存
	#后台订单操作

	args_list = [buys_car,goodsed_dic,seller,current_user.id,user_address,request.form.get('note','')]

	# executor.submit(back_submit_order,current_app._get_current_object(),,,,.id,,)
	executor.submit(back_submit_order,current_app._get_current_object(),args_list,db)
	flash('订单已提交','success')

	return redirect(url_for('user.my_order'))



#获取缩略图
@blueprint.route("/thumbnail/<path:filename>")
def get_thumbnail(filename=''):
    path = os.getcwd()+'/'+current_app.config['THUMBNAIL_FOLDER']
    return send_from_directory(path, filename)



@blueprint.route('/files/<path:filename>')
def get_image(filename=''):
    path = os.getcwd()+'/'+current_app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)


#平台简介
@blueprint.route('/introduction')
@templated()
def introduction():
	return dict()


#使用介绍
@blueprint.route('/use')
@templated()
def use():
	return dict()


#服务条款
@blueprint.route('/terms_of_service')
@templated()
def terms_of_service():
	return dict()



#再来一单 获取最近的几单订单列表
@blueprint.route('/again')
@templated()
@login_required
def again():

    user_order = UserOrder.query\
        .filter(UserOrder.users_buy==current_user)\
        .order_by(desc(UserOrder.id))\
        .limit(3).all()
        
    return dict(order=user_order)


#确认再来一单
@blueprint.route('/confirm_again/<int:id>')
@templated()
@login_required
def confirm_again(id=0):
    #根据订单获得订单销售的商品 添加到购物车
    sale = Sale.query\
        .with_entities(Sale)\
        .join(UserOrder,UserOrder.id==Sale.UserOrder_id)\
        .filter(UserOrder.id==id)\
        .all()

    #添加到购物车
    for i in sale:
        db.session.add(BuysCar(user_id=current_user.id,goods_id=i.goods_id,count=i.count))
    db.session.commit()

    red_url = url_for('.submit_order')
    return redirect(red_url)



