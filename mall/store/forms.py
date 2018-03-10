# -*- coding: utf-8 -*-
"""Stroe forms."""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class CreateStoreForm(FlaskForm):

	name = StringField(u'店铺名称', validators=[DataRequired()])
	address = StringField(u'店铺地址', validators=[DataRequired()])
	note = StringField(u'店铺简介', validators=[DataRequired()])
	contact = StringField(u'联系方式', validators=[DataRequired()])
    

    

    