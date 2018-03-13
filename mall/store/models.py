#coding=utf-8

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
    
	#店铺横幅
	seller_banner_id = relationship('SellerBanner', backref='seller')
	#仓库
	warehouse_id = relationship('Warehouse', backref='seller')

	#订单
	user_order_id = relationship('UserOrder', backref='seller')
	#进货单
	receipt_id = relationship('Receipt', backref='seller')
	goods_id = relationship('Goods', backref='seller')

	seller_info_id = relationship('SellerInfo', backref='seller')
	sale_id = relationship('Sale', backref='seller')
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
	#店铺分类
	sellers_id = reference_col('sellers')
	#产品分类
	category_id = reference_col('categorys')

	#商品名称
	title = Column(db.String(100)) 
	#原价
	original_price = Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#优惠价
	special_price = Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#详情
	note =  Column(db.UnicodeText())
	# 数量
	# count = Column(db.Integer(),default=0)
	#发布时间
	# create_time =  Column(db.DateTime,default=dt.datetime.now) 
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
	# 排序
	# sort = Column(db.Integer(),default=100)
	#条码
	ean = Column(db.String(50))
	#规格
	unit = Column(db.Integer,default=1)
	#创建时间
	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)
	#出售记录
	sale_id = relationship('Sale', backref='goodsed')
    
	

#卖家订单中心 每日信息
class SellerInfo(SurrogatePK, Model):
	__tablename__ = 'sellers_info'

	seller_id = reference_col('sellers')
	#计算时间
	Date =  db.Column(db.Date,default=time.strftime('%Y%m%d')) 
	#访客
	visitor = db.Column(db.Integer(),default=1)
	#成交额
	price = db.Column(db.Numeric(15,4))
	#订单数量
	order = db.Column(db.Integer(),default=0)


#出售的商品记录
class Sale(SurrogatePK,Model):

	__tablename__ = 'sales'
	#店铺
	seller_id = reference_col('sellers')
	#商品
	goods_id = reference_col('goodsed')
	#货位
	goods_allocation_id = reference_col('goods_allocation')
	#订单
	UserOrder_id = reference_col('user_order')
	#剩余数量
	residue_count = Column(db.Integer)

	#创建时间
	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)


#入库单
class Receipt(SurrogatePK,Model):
	__tablename__ = 'receipts'

	#供应商
	supplier = Column(db.String(100))

	#卖家
	seller_id = reference_col('sellers')

	#订单号
	number = db.Column(db.String(100)) 
	#下单时间
	buy_time = Column(db.DateTime,default=dt.datetime.now)
    
	#送货时间
	send_time =  db.Column(db.DateTime) 
	#配送费
	freight = db.Column(db.Numeric(15,2),default=0)

	#优惠金额
	discount = db.Column(db.Numeric(15,2))
	#支付金额
	pay_price = db.Column(db.Numeric(15,2))
	#支付时间
	pay_time =  db.Column(db.DateTime) 
	#支付类型
	pay_type = db.Column(db.String(100)) 

	#备注
	note = db.Column(db.String(255)) 

	#状态默认0
	order_state = db.Column(db.Integer(),default=1)

	#进货的商品
	stock_id = relationship('Stock', backref='receipts')
    


#进货
class Stock(SurrogatePK,Model):

	__tablename__ = 'stocks'
	#店铺
	seller_id = reference_col('sellers')
	#商品
	goods_id = reference_col('goodsed')
	#货位
	goods_allocation_id = reference_col('goods_allocation')
	#订单
	receipts_id = reference_col('receipts')
	#数量
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

	warehouse_id = reference_col('warehouses')

	sale_id = relationship('Sale', backref='goodsed_allocation')
    


#库存
class Inventory(SurrogatePK,Model):

	__tablename__ = 'inventory'
	#商品
	good_id = reference_col('goodsed')
	#货位
	goods_allocation_id = reference_col('goods_allocation')

	count = Column(db.Integer,default=0)





