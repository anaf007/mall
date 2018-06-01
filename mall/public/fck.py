from flask import request,url_for,current_app,send_from_directory,\
    redirect
from werkzeug.utils import secure_filename
from flask_login import current_user
from mall.extensions import ckeditor,csrf_protect,wechat
from mall.utils import send_email
from log import logger

from .models import UserOrder,BuysCar
from mall.store.models import Seller,Sale
from mall.user.models import User

import datetime,os,time,random

from .import blueprint


@blueprint.route('/ckeditorfiles/<path:filename>')
@csrf_protect.exempt
def ckeditorfiles(filename):
    path = os.getcwd()+'/'+current_app.config['CKEDITOR_FILE_UPLOAD_URL']
    return send_from_directory(path, filename)


@blueprint.route('/upload', methods=['GET','POST'])
@csrf_protect.exempt
@ckeditor.uploader
def upload():
    f = request.files.get('upload')
    filename = secure_filename(f.filename)

    dataetime = datetime.datetime.today().strftime('%Y%m%d')
    file_dir = '%s/%s/'%(current_user.id,dataetime)
    
    if not os.path.isdir(current_app.config['CKEDITOR_FILE_UPLOAD_URL']+file_dir):
        os.makedirs(current_app.config['CKEDITOR_FILE_UPLOAD_URL']+file_dir)
    
    f.save(current_app.config['CKEDITOR_FILE_UPLOAD_URL'] +file_dir+filename)
    filename = file_dir+filename

    url = url_for('.ckeditorfiles', filename=filename)
    return url


#后台操作订单
# @blueprint.context_processor
def back_submit_order(cap=[],args_list=[],db=[]):

    try:
        
        #出库单号
        with cap.app_context():
        
            choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
            str_time =  time.time()
            number_str = 'T'
            number_str += str(int(int(str_time)*1.301))
            for i in range(4):
                number_str += random.choice(choice_str)

            try:
                
                #出库单
                user_order = UserOrder()
                user_order.user_id = args_list[3]
                user_order.receive_name = args_list[4].name
                user_order.receive_phone = args_list[4].phone
                user_order.receive_address = args_list[4].address
                user_order.number = number_str
                user_order.note = args_list[5]
                user_order.seller_id =  args_list[0][0][5]

                db.session.add(user_order)

            except Exception as e:
                send_email(f'用户提交订单，创建出库单错误。{e}')
                logger.error(f'用户提交订单，创建出库单错误。{e}')

            count_price = 0
            goods_number = 0

            # 减去库存   #buys_car 购物车   goodsed_dic 货位商品

            try:
                #购物车
                for i in args_list[0]:
                    count = i.count
                    for j in args_list[1][str(i[2])]:

                        # print(j)

                        #销售的商品记录
                        sale = Sale()
                        sale.seller_id = args_list[2]
                        sale.goods_id = i[2]
                        sale.goods_title = i[3]
                        sale.original_price = i[4]
                        sale.special_price = i[10]
                        sale.main_photo = i[9]

                        sale.count = i[1]
                        # sale.residue_count = seller
                        sale.user_order = user_order
                        sale.seller_id = i[5]


                        #如果库存数量大于购物车数量
                        if j[0].count - count >= 0:
                            #出售记录表
                            sale.residue_count = j[0].count - count
                            sale.goods_allocation_name = j[1].name
                            
                            #更新库存
                            j[0].count = j[0].count - count
                            # db.session.add(j)

                            local_object = db.session.merge(j[0])
                            db.session.add(local_object)
                            # j.save(False)
                            break;

                        #如果库存数量少于购物车数量
                        if j[0].count - count < 0:
                            sale.residue_count = 0
                            sale.goods_allocation_name = j[1].name
                            count = count - j[0].count
                            
                            #删除库存
                            # j.delete(False)
                            db.session.delete(j[0])

                        db.session.add(sale)

                    #计算总价 1数量  4销售价格
                    count_price += i[1]*i[4]
                    #商品种类数量
                    goods_number += 1

            except Exception as e:
                logger.error('用户提交订单库存相减错误。')
                send_email(f'用户提交订单库存相减错误。{e}')
            


            #7运费  8最低配送额
            
            if count_price < args_list[0][0][8]:
                count_price += args_list[0][0][7]
                user_order.freight = args_list[0][0][7]
            else:
                user_order.freight = 0

            user_order.pay_price = count_price
            user_order.goods_number = goods_number

            db.session.add(user_order)
            # end减去库存

            try:
                db.session.commit()
                
                # 删除购物车
                for i in BuysCar.query.filter_by(user_id=args_list[3]).all():
                    db.session.delete(i)
                db.session.commit()
                #end删除购物车

                seller = Seller.query\
                    .with_entities(Seller,User)\
                    .join(User,User.id==Seller.user_id)\
                    .filter(Seller.id==args_list[0][0][5])\
                    .first()


                #微信客服消息
                try:
                    teacher_wechat = seller[1].wechat_id
                    msg_title = '您有新的销售信息，回复"so%s"查看订单信息。'%user_order.id
                    wechat.message.send_text(teacher_wechat,msg_title)
                except Exception as e:
                    if seller[0].email:
                        send_email('你有新的销售订单，请进入公众号隔壁小超市查看。',seller[0].email)
                    # logger.info(f'用户提交订单 无法微信通知商家 {e}')

            except Exception as e:
                logger.error(f'用户提交订单db提交 删除购物车 错误{e}')
                send_email(f'用户提交订单db提交 删除购物车{e}')
                db.session.rollback()



    except Exception as e:
        logger.info(f'用户提交订单 后端异步错误 {e}')
        send_email(f'用户提交订单 后端异步错误{e}')





