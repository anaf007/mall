# -*- coding: utf-8 -*-
"""Superadmin forms."""
from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired

from mall.user.models import User
from .models import Category


class AddCategoryForm(FlaskForm):

    name = StringField(u'名称', validators=[DataRequired()])
    ico = StringField(u'分类图标')
    sort = IntegerField(u'排序', validators=[DataRequired()])
    active = BooleanField(u'状态',default=True)
    pid = SelectField(u'上级栏目',choices=[(-1,u'顶级栏目')],coerce=int)


    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(AddCategoryForm, self).__init__(*args, **kwargs)
        self.pid.choices = self.pid.choices+[(obj.id, obj.name) for obj in Category.query.order_by('sort').all()]
        

