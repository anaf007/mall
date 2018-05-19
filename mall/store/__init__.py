# -*- coding: utf-8 -*-
"""The store module, including the homepage and user auth."""
from flask import Blueprint,url_for
from mall.extensions import wechat

blueprint = Blueprint('store', __name__, url_prefix='/store')

from . import views, models,views_json,errors  # noqa



def creat_store_emenu():
    wechat.menu.create({"button":[
        {"type":"view","name":"买买买","url":'%s'%url_for('public.home',_external=True)},\

        {"type":"view","name":"我的","sub_button":[
            {
                "type":"view",
                "name":"购物车",
                "url":'%s'%url_for('user.my_buys_car',_external=True)
            },
            {
                "type":"view",
                "name":"订单",
                "url":'%s'%url_for('user.my_order',_external=True)
            },
            {
                "type":"view",
                "name":"收货地址",
                "url":'%s'%url_for('user.my_order',_external=True)
            },
            {
                "type":"view",
                "name":"商家主页",
                "url":'%s'%url_for('store.home',_external=True)
            },
        ]},\

        {"type":"view","name":"用户服务","sub_button":[
            {
                "type":"view",
                "name":"平台简介",
                "url":'%s'%url_for('public.introduction',_external=True)
            },
            {
                "type":"view",
                "name":"使用介绍",
                "url":'%s'%url_for('public.use',_external=True)
            },
            {
                "type":"view",
                "name":"服务条款",
                "url":'%s'%url_for('public.terms_of_service',_external=True)
            },
        ]},\
        
    ]})

