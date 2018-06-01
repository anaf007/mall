from flask import jsonify,request
from flask_login import login_required,current_user

from . import blueprint

from mall.superadmin.models import BaseProducts
from mall.extensions import db
from .models import Goods,GoodsAllocation
from mall.public.models import UserOrder

# import json,simplejson
import simplejson as json
import datetime,time



#添加商品获取系统商品基础数据
@blueprint.route('/get_base_product')
@blueprint.route('/get_base_product/<int:id>')
@login_required
def get_base_product(id=0):

    wd = request.args.get('wd','0')

    base_product =  BaseProducts.query\
        .with_entities(BaseProducts.id,BaseProducts.title,BaseProducts.original_price\
            ,BaseProducts.special_price,BaseProducts.main_photo)\
        .filter(BaseProducts.title.ilike(f'%{wd}%') | BaseProducts.ean.ilike(f'%{wd}%'))\
        .limit(10).all()

    return json.dumps({'cb':base_product})


#入库单添加商品获取商品名称
@blueprint.route('/get_receipt_goods_name')
@blueprint.route('/get_receipt_goods_name/<int:id>')
@login_required
def get_receipt_goods_name(id=0):

    wd = request.args.get('wd','0')

    base_product =  Goods.query\
        .with_entities(Goods.id,Goods.title,Goods.ean)\
        .filter(db.or_(Goods.title.ilike(f'%{wd}%'),Goods.ean.ilike(f'%{wd}%')))\
        .filter(Goods.seller==current_user.seller_id[0])\
        .all()[0:10]

    return json.dumps({'cb':base_product})


#入库单添加商品获取货位名称
@blueprint.route('/get_receipt_location_name')
@blueprint.route('/get_receipt_location_name/<int:id>')
@login_required
def get_receipt_location_name(id=0):

    wd = request.args.get('wd','0')

    base_location =  GoodsAllocation.query\
        .with_entities(GoodsAllocation.id,GoodsAllocation.name)\
        .filter(db.or_(GoodsAllocation.name.ilike(f'%{wd}%')))\
        .filter(GoodsAllocation.users==current_user)\
        .all()[0:10]

    return json.dumps({'cb':base_location})


#获得系统单个商品基础数据
@blueprint.route('/get_base_product_one')
@blueprint.route('/get_base_product_one/<int:id>')
@login_required
def get_base_product_one(id=0):
    wd = request.args.get('wd','0')

    wd = wd.split('|')[0]

    base_product = BaseProducts.query\
        .with_entities(BaseProducts.id,BaseProducts.title,BaseProducts.original_price\
            ,BaseProducts.special_price,BaseProducts.main_photo,BaseProducts.note,BaseProducts.ean,BaseProducts.unit)\
        .filter_by(id=int(wd)).first()

    return json.dumps({'pr':base_product})


#经营数据销售数据
@blueprint.route('/get_operating_json')
@login_required
def get_operating_json():

    #当天
    start_day = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    end_day = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    day_order = UserOrder.query.filter_by(seller_id=current_user.seller_id[0].id).filter(UserOrder.buy_time.between(start_day,end_day)).all()

    #本周
    start_weekday = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    # end_weekday = datetime.date.today()
    end_weekday = datetime.datetime.now()  
    weekday_order = UserOrder.query.filter_by(seller_id=current_user.seller_id[0].id).filter(UserOrder.buy_time.between(start_weekday,end_weekday)).all()

    #本月
    start_mon = datetime.date.today() - datetime.timedelta(days=datetime.datetime.now().day - 1)
    mon_order = UserOrder.query.filter_by(seller_id=current_user.seller_id[0].id).filter(UserOrder.buy_time.between(start_mon,end_weekday)).all()

    #计算天
    day_original_price = 0
    day_special_price = 0
    for i in day_order:
        for j in i.sale_id:
            if not j.original_price:
                j.original_price = 0
            if not j.special_price:
                j.special_price = 0
            day_original_price += j.original_price*j.count
            day_special_price += j.special_price*j.count


    #计算周
    weekday_original_price = 0
    weekday_special_price = 0
    for i in weekday_order:
        for j in i.sale_id:
            if not j.original_price:
                j.original_price = 0
            if not j.special_price:
                j.special_price = 0
            weekday_original_price += j.original_price*j.count
            weekday_special_price += j.special_price*j.count

    #计算月
    mon_original_price = 0
    mon_special_price = 0
    for i in mon_order:
        for j in i.sale_id:
            if not j.original_price:
                j.original_price = 0
            if not j.special_price:
                j.special_price = 0
            mon_original_price += j.original_price*j.count
            mon_special_price += j.special_price*j.count

    day_prict = [day_original_price,day_special_price]
    weekday_prict = [weekday_original_price,weekday_special_price]
    mon_prict = [mon_original_price,mon_special_price]

    return json.dumps({'price':[day_prict,weekday_prict,mon_prict]})





