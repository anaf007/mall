"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, abort,Response, jsonify
from flask_login import login_required, login_user, logout_user,current_user
from sqlalchemy import desc

from collections import OrderedDict

from mall.extensions import login_manager,db
from mall.user.forms import RegisterForm
from mall.user.models import User
from mall.superadmin.models import Category
from mall.store.models import Seller,Goods,Inventory,GoodsAllocation,Sale
from mall.utils import flash_errors,templated
from .models import Follow,BuysCar,UserAddress,UserOrder
from  . import blueprint

import random,time




@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/')
@templated()
@login_required
def home():
    """Home page."""
    
    seller = Seller.query.with_entities(User.wechat_id,Seller.id).join(User,User.id==Seller.user_id).filter(Seller.id==1).first()
    print(seller)

    follow = Follow.query.filter_by(users=current_user).all()
    len_follow = len(follow)
    if len_follow>0 and len_follow<=1:
    	return redirect(url_for('.show_store',seller_id=follow[0].id))
    if len_follow<1:
    	flash('您还未关注店铺。')
    return dict()


#显示店铺
@blueprint.route('/show_store/<int:seller_id>')
@templated()
@login_required
def show_store(seller_id=0):

	#显示主页商品
    goodsed = Goods.query\
    	.with_entities(Goods.id,Goods.title,Goods.original_price,\
    			Goods.category_id,Category.sort,Seller.name,\
    			Seller.contact,Category.name)\
    	.join(Category,Goods.category_id==Category.id)\
    	.join(Seller,Seller.id==Goods.sellers_id)\
    	.join(Follow,Follow.seller_id==Seller.id)\
    	.filter(Seller.id==seller_id)\
    	.order_by(Category.sort)\
    	.all()

    goodsed_dic = {}
    seller_name =  goodsed[0][5]
    seller_phone=  goodsed[0][6]

    for i in goodsed:
    	value_list = [i.id,i.title,i.original_price,i.category_id,i.name]
    	if goodsed_dic.__contains__(str(i.sort)+'_'+str(i.category_id)):
    		goodsed_dic[str(i.sort)+'_'+str(i.category_id)].append(value_list)
    	else:
    		goodsed_dic[str(i.sort)+'_'+str(i.category_id)] = [value_list]
    
    #字典排序
    goodseds = [(k,goodsed_dic[k]) for k in sorted(goodsed_dic.keys())]

    #end显示主页商品

    #购物车
    buys_car = BuysCar.query\
    	.with_entities(BuysCar.id,BuysCar.count,Goods.title,Goods.original_price,Goods.id)\
    	.join(Goods,Goods.id==BuysCar.goods_id)\
    	.filter(BuysCar.users==current_user)\
    	.all()

    return dict(seller=[seller_name,seller_phone],goods=goodseds,buys_car=buys_car)


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



@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))





#购物车提交订单
@blueprint.route('/submit_order')
@templated()
def submit_order():
	#购物车信息
	# buys_car = BuysCar.query.filter_by(users=current_user).all()
	buys_car = BuysCar.query\
		.with_entities(\
			BuysCar.id,BuysCar.count,\
			Goods.id,Goods.title,Goods.original_price,\
			Seller.freight,Seller.max_price_no_freight)\
		.join(Goods,Goods.id==BuysCar.goods_id)\
		.join(Seller,Seller.id==Goods.sellers_id)\
		.filter(BuysCar.users==current_user)\
		.all()

	#如果购物车为空
	if not buys_car:
		flash('购物车中无货，不能提交订单。')
		return redirect(url_for('public.home'))

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
	user_address = UserAddress.query.get(request.form.get('user_address',0))
	if not user_address:
		flash('您未添加收货地址，请填写填写收货地址。')
		abort(401)

	buys_car = BuysCar.query\
		.with_entities(
			BuysCar.id,BuysCar.count,BuysCar.goods_id,\
			Goods.title,Goods.original_price,Goods.sellers_id,\
			Seller.name,Seller.freight,Seller.max_price_no_freight\
		)\
		.join(Goods,Goods.id==BuysCar.goods_id)\
		.join(Seller,Seller.id==Goods.sellers_id)\
		.filter(BuysCar.users==current_user)\
		.all()
	if not buys_car:
		return redirect(url_for('public.home'))


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
		.filter(Inventory.goods_id.in_(all_goodsed_id))\
		.join(GoodsAllocation,GoodsAllocation.id==Inventory.goods_allocation_id)\
		.order_by(GoodsAllocation.sort)\
		.all()


	goodsed_dic = {}
	for i in all_goods:
		if goodsed_dic.__contains__(str(i.goods_id)):
			goodsed_dic[str(i.goods_id)].append(i)
		else:
			goodsed_dic[str(i.goods_id)] = [i]	
	
	
	for i in buys_car:
		count = i.count
		try:
			for j in goodsed_dic[str(i[2])]:
				#库存数减去购物车数量
				if j.count - count >= 0:
					break;
				if j.count - count < 0:
					count = count - j.count
			else:
				abort(Response('店家该商品 "%s" 库存不足'%i[3]))

		except:
			abort(Response('店家该商品 "%s  "库存不足'%i[3]))
			
	#end检查商家是否足够库存

	#出库单号
	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	str_time =  time.time()
	number_str = 'T'
	number_str += str(int(int(str_time)*1.301))
	for i in range(4):
		number_str += random.choice(choice_str)

	#出库单
	user_order = UserOrder()
	user_order.user_id = current_user.id
	# user_order.receive = user_address.id
	user_order.receive_name = user_address.name
	user_order.receive_phone = user_address.phone
	user_order.receive_address = user_address.address
	user_order.number = number_str
	user_order.note = request.form.get('note','')
	user_order.seller_id = buys_car[0][5]

	#暂时提交 否则没有id值
	db.session.add(user_order)

	count_price = 0
	goods_number = 0

	# 减去库存   #buys_car 购物车   goodsed_dic 货位商品
	for i in buys_car:
		count = i.count
		for j in goodsed_dic[str(i[2])]:

			#销售的商品记录
			sale = Sale()
			sale.seller_id = seller
			sale.goods_id = i[2]
			sale.count = i[1]
			sale.residue_count = seller
			sale.user_order = user_order
			sale.seller_id = i[5]
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

		#计算总价 1数量  4销售价格
		count_price += i[1]*i[4]
		#商品种类数量
		goods_number += 1

	#7运费  8最低配送额
	if count_price < buys_car[0][8]:
		count_price += buys_car[0][7]
		user_order.freight = buys_car[0][7]
	else:
		user_order.freight = 0

	user_order.pay_price = count_price
	user_order.goods_number = goods_number

	db.session.add(user_order)

	# end减去库存

	try:
		db.session.commit()
		flash('订单提交成功','success')

		# 删除购物车
		for i in BuysCar.query.filter_by(users=current_user).all():
			db.session.delete(i)
		db.session.commit()
		#end删除购物车

		#微信客服消息
		try:
			seller = Seller.query\
				.with_entities(User.wechat_id,Seller.id)\
				.join(User,User.id==Seller.user_id)\
				.filter(Seller.id==buys_car[0][5])\
				.first()
			teacher_wechat = seller[0]
			msg_title = '您有新的销售信息，回复"so%s"查看订单信息。'%user_order.id
			wechat.message.send_text(teacher_wechat,msg_title)
		except OSError as err:
			return str(err)

	

	except OSError as err:
		db.session.rollback()
		return str(err)

	return redirect(url_for('user.my_order'))





