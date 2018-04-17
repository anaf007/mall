#coding=utf-8

from flask import request,current_app
from flask_wechatpy import wechat_required
from wechatpy.replies import TextReply,ArticlesReply,create_reply,ImageReply

from . import blueprint,wechat
from mall.extensions import csrf_protect

from mall.public.models import UserOrder
from mall.store.models import Serller
from mall.user.models import User


def createmenu():
    wechat.menu.create({"button":[
        {"type":"view","name":"买买买","url":'http://mall.anaf.cn'},\

        {"type":"view","name":"用户服务","sub_button":[
            {
                "type":"view",
                "name":"我的订单",
                "url":'http://mall.anaf.cn/users/my_order'
            },
            {
                "type":"view",
                "name":"我的购物车",
                "url":'http://mall.anaf.cn/users/my_buys_car'
            },

        ]},\
        
    ]})


#微信获取token
@blueprint.route('/token',methods=['GET'])
@wechat_required
def token_get():
    signature = request.args.get('signature','')
    timestamp = request.args.get('timestamp','')
    nonce = request.args.get('nonce','')
    echostr = request.args.get('echostr','')
    token = current_app.config['SCHOOL_WECHAT_TOKEN']
    sortlist = [token, timestamp, nonce]
    sortlist.sort()
    sha1 = hashlib.sha1()
    map(sha1.update, sortlist)
    hashcode = sha1.hexdigest()
    try:
        check_signature(token, signature, timestamp, nonce)
    except InvalidSignatureException:
        abort(403)
    return echostr



#微信token信息提交
@csrf_protect.exempt
@blueprint.route('/token',methods=['POST'])
@wechat_required
def token_post():
    msg = request.wechat_msg
    reply = ''
    if msg.type == 'text':

        event_str = msg.content[0:2]
        str_id = msg.content[2:]

        #店家显示订单详情
        if event_str == 'so':

            users_order = UserOrder.query\
                .with_entities(UserOrder,Serller,User)\
                .join(Serller,Serller.id==UserOrder.seller_id)\
                .join(User,User.id==Serller.user_id)\
                .filter(User.wechat_id==msg.source)\
                .filter(UserOrder.id==str_id)\
                .first()

            if users_order:
                textreply_str = '您有新的销售订单。<a href="">点击查看</a>'
                
            else:
                textreply_str = '输入错误'
                

            reply = TextReply(content='', message=msg)
            return reply

    return ''

