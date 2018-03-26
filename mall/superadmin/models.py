#coding=utf-8
from mall.database import Column, Model, SurrogatePK, db, reference_col, relationship

import datetime as dt

#系统更新版本号
class SystemVersion(SurrogatePK,Model):

	__tablename__ = 'system_versions'
	#版本号
	number = Column(db.String(20))
	#标题
	title = Column(db.String(100))
	#描述
	summary = Column(db.String(200))
	#内容
	context = Column(db.UnicodeText)

	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)
	

#基础的商品数据，当输入名称自动查找关联，省去了店家的输入，管理员操作
class BaseProducts(SurrogatePK, Model):

	__tablename__ = 'base_products'

	#商品名称
	name = Column(db.String(255)) 
	#原价
	original_price = Column(db.Numeric(15,2))
	#优惠价
	special_price = Column(db.Numeric(15,2))
	#详情
	note =  Column(db.UnicodeText())
	#分类
	category_id = Column(db.Integer())
	#附加字段
	attach_key = Column(db.String(200))
	#附加值
	attach_value = Column(db.String(500))


#商品分类
class Category(SurrogatePK,Model):

	__tablename__ = 'categorys'


	#:自身上级，引用自身无限级分类
	parent_id = reference_col('categorys')

	children = relationship("Category",lazy="joined",join_depth=2)
	goods_id = relationship('Goods', backref='category')
    
	#分类名称
	name = Column(db.String(100)) 
	#分类图标
	ico = Column(db.String(100)) 
	#排序
	sort = Column(db.Integer(),default=100)
	#状态
	status = Column(db.Integer(),default=1)
	#是否启用
	active = Column(db.Boolean,default=True)



	


