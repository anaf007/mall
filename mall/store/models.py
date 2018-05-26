from mall.database import Column, Model, SurrogatePK, db, reference_col, relationship

import datetime as dt
import time


#卖家
class Seller(SurrogatePK, Model):

	__tablename__ = 'sellers'

	user_id = reference_col('users')

	#店铺名称
	name = Column(db.String(100)) 
	#店铺地址
	address = Column(db.String(255)) 
	#店铺LOGO
	logo = Column(db.String(255)) 
	#是否自营 1自营  默认0 
	self_business = Column(db.Integer(),default=0)
	#评价总分数
	evaluate = Column(db.Integer())
	#评价总商品数量，得出平均店铺评分
	evaluate_count = Column(db.Integer())
	#店铺位置  地图坐标
	address_map = Column(db.String(100)) 
	#店铺状态,默认1
	status = Column(db.Integer(),default=1)
	#是否启用
	active = Column(db.Boolean(),default=True)
	#店铺备注
	note = Column(db.String(255)) 
	#创建时间
	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)
	#联系方式 
	contact = Column(db.String(255)) 
	#申请店铺默认不启用，管理员同意
	enable = Column(db.Boolean,default=False)

	#每日最大订单
	max_order = Column(db.Integer,default=10)
	#每日最大交易额
	max_price = Column(db.Integer,default=500)
	#最大仓库
	max_warehouse = Column(db.Integer,default=1)
	#最大货位
	max_goods_location = Column(db.Integer,default=2)
	#商品数量
	max_goods_count = Column(db.Integer,default=20)
	#level等级
	level = Column(db.String(20),default=u'免费会员')


	#运费
	freight = Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None),default=0)
	#满多少免运费
	max_price_no_freight = Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None),default=0)

	#店铺横幅
	seller_banner_id = relationship('SellerBanner', backref='seller')
	#仓库
	warehouse_id = relationship('Warehouse', backref='seller')

	#订单
	user_order_id = relationship('UserOrder', backref='seller')
	goods_id = relationship('Goods', backref='seller')

	seller_info_id = relationship('SellerInfo', backref='seller')
	sale_id = relationship('Sale', backref='seller')
	follow_id = relationship('Follow', backref='seller')
	#盘点表
	quantity_check_id = relationship('QuantityCheck', backref='seller')


#横幅
class SellerBanner(SurrogatePK, Model):
	__tablename__ = 'banners'
	
	sellers_id = reference_col('sellers')
 
	#链接  默认不允许有链接
	link =  Column(db.String(255))
	#图片地址
	photo_url =  Column(db.String(255))
	active = Column(db.Boolean(),default=True)
	#创建时间
	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)



#商品数据
class Goods(SurrogatePK, Model):

	__tablename__ = 'goodsed'

	#所属店铺
	sellers_id = reference_col('sellers')
	#产品分类
	category_id = reference_col('categorys')

	#商品名称
	title = Column(db.String(100)) 
	#销售价
	original_price = Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#优惠价进货价
	special_price = Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#详情
	note =  Column(db.UnicodeText())
	# 附加字段
	attach_key = Column(db.String(500))
	#附加值
	attach_value = Column(db.String(500))
	#商品状态
	active = Column(db.Boolean(),default=True)
	#是否出售
	is_sell = Column(db.Boolean(),default=True)
	#热门 0 不热门 1热门
	hot = Column(db.Boolean(),default=True)
	#查看次数
	click_count = Column(db.Integer(),default=0)
	#累计购买总数
	buy_count = Column(db.Integer(),default=0)
	#条码
	ean = Column(db.String(50))
	#规格
	unit = Column(db.Integer,default=1)
	#创建时间
	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)
	#首页展示图
	main_photo = Column(db.String(200))
	
	#出售记录
	# sale_id = relationship('Sale', backref='goodsed')
	#库存
	inventory_id = relationship('Inventory', backref='goodsed')
	#进货的商品
	# stock_id = relationship('Stock', backref='goodsed')
	#购物车中的商品
	buys_car_id = relationship('BuysCar', backref='goodsed')
	
    

#卖家订单中心 每日信息
class SellerInfo(SurrogatePK, Model):
	__tablename__ = 'sellers_info'

	seller_id = reference_col('sellers')
	#计算时间
	Date =  Column(db.Date,default=time.strftime('%Y%m%d')) 
	#访客
	visitor = Column(db.Integer(),default=1)
	#成交额
	price = Column(db.Numeric(15,4))
	#订单数量
	order = Column(db.Integer(),default=0)


#出售的商品记录
class Sale(SurrogatePK,Model):

	__tablename__ = 'sales'
	#店铺
	seller_id = reference_col('sellers')
	#商品 2018-04-30修改不外键商品表否则更改价格以往的都会更改。
	# goods_id = reference_col('goodsed')
	#商品名称
	goods_id = Column(db.Integer())    #不做外键    出售记录只做快照浏览
	goods_title = Column(db.String(100)) 
	#销售价
	original_price = Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#优惠价进货价
	special_price = Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#首页展示图
	main_photo = Column(db.String(200))
	#货位
	goods_allocation_name = Column(db.String(100)) 

	#订单
	UserOrder_id = reference_col('user_order')
	#出售数量
	count = Column(db.Integer)
	#货位剩余数量
	residue_count = Column(db.Integer)

	#创建时间
	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)


#入库单
class Receipt(SurrogatePK,Model):
	__tablename__ = 'receipts'

	#供应商
	supplier = Column(db.String(100))

	#卖家
	user_id = reference_col('users')

	#订单号
	number = Column(db.String(100),unique=True) 
	#下单时间
	buy_time = Column(db.DateTime,default=dt.datetime.now)
    
	#送货时间
	send_time =  Column(db.DateTime) 
	#配送费
	freight = Column(db.Numeric(15,2),default=0)

	#优惠金额
	discount = Column(db.Numeric(15,2))
	#支付金额
	pay_price = Column(db.Numeric(15,2))
	#支付时间
	pay_time =  Column(db.DateTime) 
	#支付类型 微信 现金  银行卡 其他
	pay_type = Column(db.String(100)) 
	#备注
	note = Column(db.String(255)) 
	#状态默认0
	order_state = Column(db.Integer(),default=1)

	#商品种类
	variety = Column(db.Integer)
	#商品总数量
	goods_sum =  Column(db.Integer)
	#总价
	price_sum = Column(db.Numeric(15,2),default=0)

	#进货的商品
	stock_id = relationship('Stock', backref='receipts')
    

#进货货
class Stock(SurrogatePK,Model):

	__tablename__ = 'stocks'
	#用户
	user_id = reference_col('users')

	#商品名称
	goods_id = Column(db.Integer()) 
	goods_title = Column(db.String(100)) 
	#销售价
	original_price = Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#优惠价进货价
	special_price = Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#首页展示图
	main_photo = Column(db.String(200))
	#货位
	goods_allocation_name = Column(db.String(100)) 

	#订单
	receipts_id = reference_col('receipts')
	#进货数量
	stock_count = Column(db.Integer)
	#仓库数量
	residue_count = Column(db.Integer)

	#创建时间
	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)


#仓库
class Warehouse(SurrogatePK,Model):

	__tablename__ = 'warehouses'
	#仓库名称
	name = Column(db.String(20)) 
	#仓库状态0正常仓，1库存仓，2退货仓
	state = Column(db.Integer,default=1)
	#仓库别名
	nickname = Column(db.String(20)) 
	#是否可用
	active = Column(db.Boolean,default=1)
	#创建时间
	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)

	goods_allocation_id = relationship('GoodsAllocation', backref='warehouse')

	sellers_id = reference_col('sellers')
    

#货位
class GoodsAllocation(SurrogatePK,Model):

	__tablename__ = 'goods_allocation'
	#货位名称
	name = Column(db.String(50)) 
	#排序
	sort = Column(db.Integer,default=100)
	#货位备注
	note = Column(db.String(100))
	#所属仓库
	warehouse_id = reference_col('warehouses')
	#所属用户，不然每次查询都要join很多关联
	user_id = reference_col('users')

	# sale_id = relationship('Sale', backref='goodsed_allocation')
	#库存
	inventory_id = relationship('Inventory', backref='goods_allocation')
	#出售的商品
	# stock_id = relationship('Stock', backref='goods_allocation')
	

#库存
class Inventory(SurrogatePK,Model):

	__tablename__ = 'inventory'


	#商品
	goods_id = reference_col('goodsed')
	#货位
	goods_allocation_id = reference_col('goods_allocation')

	count = Column(db.Integer,default=0)

	note = Column(db.String(200))

	user_id = reference_col('users')


#盘点表
class QuantityCheck(SurrogatePK,Model):
	__tablename__ = 'quantity_check'

	#盘点标题
	title = Column(db.String(50))

	seller_id = reference_col('sellers')
	users_id = reference_col('users')

	created_at = Column(db.DateTime,default=dt.datetime.now)  
	#商品种类数量
	count = Column(db.Integer,default=0)

	#盘点表
	quantity_check_id = relationship('QuantityCheckGoods', backref='quantity_checks')
    

#盘点的商品
class QuantityCheckGoods(SurrogatePK,Model):
	__tablename__ = 'quantity_check_goods'

	quantity_check_id = reference_col('quantity_check')
	#数量
	count = Column(db.Integer,default=0)
	#位置
	location = Column(db.String(50))
	#商品名称 ，不外键
	goods_name = Column(db.String(50))
	#库存id  不用外键
	inventory_id = Column(db.Integer())
	#是否已提交更改库存
	submit_change = Column(db.Boolean,default=False)
	#盘点后的数量
	count_check = Column(db.Integer,default=0)
    







