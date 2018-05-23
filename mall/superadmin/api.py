
from .models import Category,BaseProducts
from ..store.models import Seller
from . import blueprint

from mall.extensions import api_manager


api_manager.create_api(Category,
    methods=['GET'],
    collection_name='category',
    url_prefix='/api/v1/superadmin',
    include_columns=['id','name','ico','sort','status','active'],
    results_per_page=20,
    code=0,
)

api_manager.create_api(BaseProducts,
    methods=['GET'],
    collection_name='base_products',
    url_prefix='/api/v1/superadmin',
    include_columns=[
        'id',
        'title',
        'original_price',
        'special_price',
        'attach_key',
        'attach_value',
        'main_photo',
        'ean',
        'unit',
    ],
    results_per_page=20,
    code=0,
)

api_manager.create_api(Seller,
    methods=['GET'],
    collection_name='seller',
    url_prefix='/api/v1/superadmin',
    include_columns=[
        'id',
        'name',
        'address',
        'status',
        'active',
        'note',
        'created_at',
        'contact',
        'enable',
        'max_order',
        'max_price',
        'max_warehouse',
        'max_goods_location',
        'max_goods_count',
        'freight',
        'max_price_no_freight',
    ],
    results_per_page=20,
    code=0,
)

   
