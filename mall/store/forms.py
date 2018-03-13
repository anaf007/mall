# -*- coding: utf-8 -*-
"""Stroe forms."""
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField,DecimalField, BooleanField, SelectField
from wtforms.validators import DataRequired

from flask_ckeditor import CKEditorField

from mall.superadmin.models import Category
from .models import Warehouse


class CreateStoreForm(FlaskForm):

	name = StringField(u'店铺名称', validators=[DataRequired()])
	address = StringField(u'店铺地址', validators=[DataRequired()])
	note = StringField(u'店铺简介', validators=[DataRequired()])
	contact = StringField(u'联系方式', validators=[DataRequired()])
    

#添加商品数据
class CommodityDataForm(FlaskForm):

	title = StringField(u'商品标题', validators=[DataRequired()])
	ean = StringField(u'商品条码', validators=[DataRequired()])
	unit = StringField(u'商品规格', validators=[DataRequired()])
	original_price = DecimalField(u'原价', validators=[DataRequired()])
	special_price = DecimalField(u'优惠价', validators=[DataRequired()])
	
	is_sell = BooleanField(u'是否出售',default=True)
	hot = BooleanField(u'热门商品',default=False)
	category = SelectField(u'上级栏目',choices=[(-1,u'请选择分类')],coerce=int)

	note = CKEditorField(u'详情')

	def __init__(self, *args, **kwargs):
		"""Create instance."""
		super(CommodityDataForm, self).__init__(*args, **kwargs)
		self.category.choices = self.category.choices+[(obj.id, obj.name) for obj in Category.query.order_by('sort').all()]
        

#添加仓库
class AddWarehouseForm(FlaskForm):
	name = StringField(u'仓库名称', validators=[DataRequired()])
	state = SelectField(u'仓库状态',choices=[(0,u'正常仓'),(1,u'库存仓'),(1,u'退货仓')],coerce=int)
	nickname = StringField(u'仓库别名', validators=[DataRequired()])
	



#添加货位
class AddLocationForm(FlaskForm):
	name = StringField(u'货位名称', validators=[DataRequired()])
	sort = StringField(u'排序',validators=[DataRequired()])
	note = StringField(u'货位备注')
	warehouse = SelectField(u'所属仓库',choices=[],coerce=int)
	
	def __init__(self, *args, **kwargs):
		"""Create instance."""
		super(AddLocationForm, self).__init__(*args, **kwargs)
		self.warehouse.choices = self.warehouse.choices+[(obj.id, obj.name) for obj in Warehouse.query.filter_by(seller=current_user.seller_id[0]).all()]
    





    


       


    