from flask import request
from . import blueprint
from flask_login import login_required

import simplejson as json
from mall.store.models import Goods



#店铺展示页搜搜产品
@blueprint.route('/get_store_product')
@login_required
def get_store_product():

    wd = request.args.get('wd','0').split('|')


    pd =  Goods.query\
        .with_entities(Goods.id,Goods.title,Goods.ean)\
        .filter(Goods.sellers_id==wd[1])\
        .filter(Goods.title.ilike(f'%{wd[0]}%') | Goods.ean.ilike(f'%{wd[0]}%'))\
        .limit(10).all()

    return json.dumps({'cb':pd})