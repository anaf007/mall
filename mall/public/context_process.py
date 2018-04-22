#coding=utf-8
from .models import *
from . import blueprint
from sqlalchemy import desc
from flask import session
from mall.superadmin.models import Category




@blueprint.context_processor
def category():
	def decorator():
		categorys = Category.query\
			.order_by('sort')\
			.filter_by(status=1)\
			.filter_by(active=True)\
			.all()
		return categorys
	return dict(get_category=decorator)


