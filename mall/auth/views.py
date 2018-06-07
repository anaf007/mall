from flask import session,redirect,request,url_for,flash,abort
from  sqlalchemy  import desc
from flask_wechatpy import oauth
from mall.extensions import db
import time,random
from flask_login import login_required,login_user,current_user,logout_user
from mall.utils import send_email
from log import logger
from mall.extensions import executor

from mall.user.models import User

from . import  blueprint
from mall.utils import templated



#自动注册 
# @blueprint.route('/autoregister')
def autoregister(wechat_id=''):
    
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

    user = []

    print(wechat_id)

    if wechat_id:
        user = User.query.filter_by(wechat_id=wechat_id).first()
    else:
        wechat_id = session.get('wechat_user_id','')
        user = User.query.filter_by(wechat_id=wechat_id).first()
        
    if user:
        login_user(user,True)
        return user 
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User.create(
            username=username,
            password=password,
            wechat_id=wechat_id,
        )
        login_user(user,True)
        return user 
    else:
        autoregister()


@blueprint.route('/autologin/<string:name>')
@blueprint.route('/autologin')
@oauth(scope='snsapi_base')
def autologin(name=''):
    try:
        if name:
            user = User.query.filter_by(username=name).first()
            login_user(user,True) if user else abort(404)
            return redirect(request.args.get('next') or url_for('public.home'))

        wechat_id = session.get('wechat_user_id','')
        if wechat_id:
            user = User.query.filter_by(wechat_id=wechat_id).first()
        else: 
            user = []
        if user :
            login_user(user,True)
        else:
            user = autoregister()

        return redirect(request.args.get('next') or url_for('public.home'))

    except Exception as e:
        logger.error(e)
        executor.submit(send_email,f'500错误{e}')
        flash(f'登录错误：{e}')
        abort(401)





@blueprint.route('/user_login',methods=['POST'])
def user_login_post():
    username = request.form.get('username','0')
    password = request.form.get('password','0')
    user = User.query.filter_by(username=username).first()
    
    if user and  user.check_password(password):
        login_user(user,True)
        return redirect(url_for(request.args.get('next')) or url_for('public.home'))
    else:
        flash('信息输入错误，没有该用户。')
        return redirect(url_for('.user_login',next=request.endpoint))



@blueprint.route('/user_login')
@templated()
def user_login():
    return dict(next=request.args.get('next'))




@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('您已退出.', 'info')
    return redirect(url_for('public.home'))


#每次登陆更新最后访问时间
@blueprint.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()

