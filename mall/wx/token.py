#coding=utf-8

from flask import request,current_app
from . import blueprint


def createmenu():
    wechat.menu.create({"button":[
        {"type":"view","name":u"请假","sub_button":[
            {
                "type":"view",
                "name":u"发起请假",
                "url":"http://school.anaf.cn/users/send_leave"
            },
        ]},\

        {"type":"view","name":u"用户服务","sub_button":[
            {
                "type":"view",
                "name":u"个人中心",
                "url":'http://school.anaf.cn/users'
            },
            {
                "type":"view",
                "name":u"平台简介",
                "url":'http://school.anaf.cn/'
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
	reply=''
	reply=TextReply(content=u'hhhhh', message=msg)

	return reply

