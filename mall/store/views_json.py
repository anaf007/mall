from flask import jsonify,request
from flask_login import login_required,current_user

from . import blueprint

from mall.superadmin.models import BaseProducts
from mall.extensions import db
from .models import Goods,GoodsAllocation

# import json,simplejson
import simplejson as json



#添加商品获取系统商品基础数据
@blueprint.route('/get_base_product')
@blueprint.route('/get_base_product/<int:id>')
@login_required
def get_base_product(id=0):

    wd = request.args.get('wd','0')

    base_product =  BaseProducts.query\
        .with_entities(BaseProducts.id,BaseProducts.title,BaseProducts.original_price\
            ,BaseProducts.special_price,BaseProducts.main_photo)\
        .filter(BaseProducts.title.ilike(f'%{wd}%'))\
        .all()[0:10]

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







