# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template,session,redirect,url_for,request
from flask_login import login_required,login_user

import time,random

from mall.user.models import User

blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')


@blueprint.route('/')
@login_required
def members():
    """List members."""
    return render_template('users/members.html')



#自动注册 
# @blueprint.route('/autoregister')
def autoregister():
	
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

	user = User.query.filter_by(username=username).first()
	if user is None:
		user = User.create(
			username=username,
			password=password,
			wechat_id=session.get('wechat_user_id',''),
		)
		login_user(user,True)
	else:
		autoregister()


@blueprint.route('/autologin')
# @oauth(scope='snsapi_userinfo')
def autologin(name=''):
	wechat_id = session.get('wechat_user_id','')
	if wechat_id:
		user = User.query.filter_by(wechat_id=session.get('wechat_user_id')).first()
	else: 
		user = []
	if user :
		login_user(user,True)
	else:
		autoregister()

	
	return redirect(request.args.get('next') or url_for('public.home'))
		
