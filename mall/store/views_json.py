from flask import jsonify,request
from . import blueprint

from mall.superadmin.models import BaseProducts

# import json,simplejson
import simplejson as json




@blueprint.route('/get_base_product')
@blueprint.route('/get_base_product/<int:id>')
def get_base_product(id=0):

    wd = request.args.get('wd','0')

    base_product =  BaseProducts.query\
        .with_entities(BaseProducts.id,BaseProducts.title,BaseProducts.original_price\
            ,BaseProducts.special_price,BaseProducts.main_photo)\
        .filter(BaseProducts.title.ilike(f'%{wd}%'))\
        .all()[0:10]

    return json.dumps({'cb':base_product})


@blueprint.route('/get_base_product_one')
@blueprint.route('/get_base_product_one/<int:id>')
def get_base_product_one(id=0):
    wd = request.args.get('wd','0')

    wd = wd.split('|')[0]

    base_product = BaseProducts.query\
        .with_entities(BaseProducts.id,BaseProducts.title,BaseProducts.original_price\
            ,BaseProducts.special_price,BaseProducts.main_photo,BaseProducts.note)\
        .filter_by(id=int(wd)).first()


    print(base_product)



    return json.dumps({'pr':base_product})







