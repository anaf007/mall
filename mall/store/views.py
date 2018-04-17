#coding=utf-8
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app, abort, Response
from sqlalchemy import desc
from mall.utils import templated, flash_errors
from flask_login import login_required,current_user
from werkzeug.datastructures import Headers
from werkzeug.utils import secure_filename

from collections import defaultdict

from .forms import *
from .models import Seller,Goods,GoodsAllocation,Inventory,Receipt,Stock
from mall.user.models import User
from mall.public.models import Follow,UserOrder
from mall.extensions import db
from mall.utils import allowed_file
import datetime as dt
import xlsxwriter,mimetypes,xlrd, os, time, random
import io
blueprint = Blueprint('store', __name__, url_prefix='/store')



@blueprint.route('/')
@templated()
@login_required
def home():

    


	try:
		store = current_user.seller_id[0]
	except e:
		flash('您未申请店铺！')
		abort(401)
	redirect_url = url_for('store.show_order',id=1,_external=True)
	if not store.enable:
		flash('您的店铺未启用，请确认管理员是否启用您的店铺。')
		abort(401)
	return dict(store=store)


#店铺申请
@blueprint.route('/create_store')
@templated()
@login_required
def create_store():
    return dict(form=CreateStoreForm())


@blueprint.route('/create_store',methods=['POST'])
@templated()
@login_required
def create_store_post():
	form = CreateStoreForm()
	if form.validate_on_submit():
		Seller.create(
			users=current_user,
			name = form.name.data,
			address = form.address.data,
			note = form.note.data,
			contact = form.contact.data,
		)
		flash('创建成功，等待管理员审核','success')
		return redirect(url_for('.home'))
	else:
		flash_errors(form)
	return dict(form=form)


#商品管理
@blueprint.route('/commodity_management')
@templated()
@login_required
def commodity_management():
    return dict(goodsed=Goods.query.filter_by(seller=current_user.seller_id[0]).all())


#商品数据
@blueprint.route('/commodity_data')
@templated()
@login_required
def commodity_data():
    return dict(form=CommodityDataForm())

#商品数据
@blueprint.route('/commodity_data',methods=['POST'])
@login_required
def commodity_data_post():
	form = CommodityDataForm()
	if form.validate_on_submit():
		Goods.create(
			title=form.title.data,
			original_price=form.original_price.data,
			special_price=form.special_price.data,
			note = form.note.data,
			is_sell = form.is_sell.data,
			hot = form.hot.data,
			ean = form.ean.data,
			unit = form.unit.data,
			seller = current_user.seller_id[0],
			category_id = form.category.data
		)
		flash('添加成功','success')
		return redirect(url_for('.commodity_data'))
	else:
		flash('添加失败','danger')
		flash_errors(form)
	return redirect(url_for('.commodity_data'))


#货位管理
@blueprint.route('/location_management')
@templated()
@login_required
def location_management():
	goods_allocation = GoodsAllocation.query.filter_by(users=current_user).order_by('sort').all()
	return dict(goods_allocation=goods_allocation)


#添加仓库
@blueprint.route('/add_warehouse')
@templated()
@login_required
def add_warehouse():
    return dict(form=AddWarehouseForm())


#添加仓库
@blueprint.route('/add_warehouse',methods=['POST'])
@login_required
def add_warehouse_post():
	form = AddWarehouseForm()
	state = form.state.data
	max_warehouse = current_user.seller_id[0].max_warehouse
	if max_warehouse<=1:
		if state!=0:
			flash('您只允许开通“正常仓”。请重新选择。')
			return redirect(url_for('.add_warehouse'))
	if max_warehouse<=2:
		if state==2 :
			flash('您只允许开通“正常仓”和“库存仓”。请重新选择。')
			return redirect(url_for('.add_warehouse'))
	if Warehouse.query.filter_by(seller=current_user.seller_id[0]).count()>=max_warehouse:
		flash('您账号最大允许添加:%s个仓库，目前已经有了这么多个不能再添加了。'%str(max_warehouse))
		return redirect(url_for('.add_warehouse'))


	if form.validate_on_submit():
		Warehouse.create(
			name=form.name.data,
			nickname=form.nickname.data,
			seller = current_user.seller_id[0],
			state = state,
		)
		flash('添加成功','success')
		return redirect(url_for('.location_management'))
	else:
		flash('添加失败','danger')
		flash_errors(form)
	return redirect(url_for('.location_management'))


#添加货位
@blueprint.route('/add_location')
@templated()
@login_required
def add_location():
    return dict(form=AddLocationForm())

@blueprint.route('/add_location',methods=['POST'])
@login_required
def add_location_post():
	form = AddLocationForm()
	max_goods_location = current_user.seller_id[0].max_goods_location
	goodsed_allocation_count = GoodsAllocation.query \
		.filter_by(users=current_user) \
		.count() 

	if goodsed_allocation_count>=max_goods_location:
		flash('您账号最大允许添加:%s个货位，目前已经有了这么多个不能再添加了。'%str(max_goods_location))
		return redirect(url_for('.add_location'))


	if form.validate_on_submit():
		GoodsAllocation.create(
			name = form.name.data,
			sort = form.sort.data,
			note = form.note.data,
			warehouse_id = form.warehouse.data,
			users = current_user
		)
		flash('添加成功','success')
		return redirect(url_for('.add_location'))
	else:
		flash('添加失败','danger')
		flash_errors(form)
	return redirect(url_for('.add_location'))


@blueprint.route('/toexcel_location')
@login_required
def toexcel_location():
    goods_allocation = GoodsAllocation.query.filter_by(users=current_user).order_by('sort').all()
    column_names = ['编号','货位名称','排序','货位备注','所属仓库ID','所属仓库名称']

    try:
        response = Response()
        response.status_code = 200

        output = io.StringIO()

        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('sheet')

        for i,x in enumerate(column_names):
        	worksheet.write(0,i,x)
        for i,x in enumerate(goods_allocation):
        	worksheet.write(i+1,0,x.id)
        	worksheet.write(i+1,1,x.name)
        	worksheet.write(i+1,2,x.sort)
        	worksheet.write(i+1,3,x.note)
        	worksheet.write(i+1,4,x.warehouse_id)
        	worksheet.write(i+1,5,x.warehouse.name)

        workbook.close()
        output.seek(0)
        response.data = output.read()

        file_name = 'goods_allocation_{}.xlsx'.format(dt.datetime.now())
        mimetype_tuple = mimetypes.guess_type(file_name)

        response_headers = Headers({
                'Pragma': "public",  # required,
                'Expires': '0',
                'Charset': 'UTF-8',
                'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
                'Cache-Control': 'private',  # required for certain browsers,
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'Content-Disposition': 'attachment; filename=\"%s\";' % file_name,
                'Content-Transfer-Encoding': 'binary',
                'Content-Length': len(response.data)
            })

        if not mimetype_tuple[1] is None:
            response.update({
                    'Content-Encoding': mimetype_tuple[1]
                })

        response.headers = response_headers
        response.set_cookie('fileDownload', 'true', path='/')
        return response

    except Exception as e:
        return str(e)

    
#导出商品基础数据
@blueprint.route('/toexcel_commodity_data')
@login_required
def toexcel_commodity_data():
    goodsed = Goods.query.filter_by(seller=current_user.seller_id[0]).all()
    column_names = ['编号','商品名称','条码','规格','原价','优惠价','是否出售','是否热门','查看次数']

    try:
        response = Response()
        response.status_code = 200

        output = io.StringIO()

        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('sheet')

        for i,x in enumerate(column_names):
        	worksheet.write(0,i,x)
        for i,x in enumerate(goodsed):
        	worksheet.write(i+1,0,x.id)
        	worksheet.write(i+1,1,x.title)
        	worksheet.write(i+1,2,x.ean)
        	worksheet.write(i+1,3,x.unit)
        	worksheet.write(i+1,4,x.original_price)
        	worksheet.write(i+1,5,x.special_price)
        	if x.is_sell:
        		worksheet.write(i+1,6,'是')
        	else:
        		worksheet.write(i+1,6,'否')
        	if x.hot:
        		worksheet.write(i+1,7,'是')
        	else:
        		worksheet.write(i+1,7,'否')
        	worksheet.write(i+1,8,x.click_count)


        workbook.close()
        output.seek(0)
        response.data = output.read()

        file_name = 'goods_{}.xlsx'.format(dt.datetime.now())
        mimetype_tuple = mimetypes.guess_type(file_name)

        response_headers = Headers({
                'Pragma': "public",  # required,
                'Expires': '0',
                'Charset': 'UTF-8',
                'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
                'Cache-Control': 'private',  # required for certain browsers,
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'Content-Disposition': 'attachment; filename=\"%s\";' % file_name,
                'Content-Transfer-Encoding': 'binary',
                'Content-Length': len(response.data)
            })

        if not mimetype_tuple[1] is None:
            response.update({
                    'Content-Encoding': mimetype_tuple[1]
                })

        response.headers = response_headers
        response.set_cookie('fileDownload', 'true', path='/')
        return response

    except Exception as e:
        return str(e)

    
#进货入库
@blueprint.route('/stock')
@templated()
@login_required
def stock():
	form=StockForm()
	recript = Receipt.query.filter_by(users=current_user).order_by(desc('id')).all()
	return dict(form=form,recript=recript)

#原始入库单  带表格文件
@blueprint.route('/stock',methods=['POST'])
@login_required
def stock_post():
	form=StockForm()
	if not form.validate_on_submit():
		flash('添加失败','danger')
		flash_errors(form)
		return redirect(url_for('.stock'))

	f = request.files['excel']
	filename = secure_filename(f.filename)
	if not filename:
		flash('添加失败文件名错误或未选择文件','danger')
		return redirect(url_for('.stock'))
	if not allowed_file(f.filename,'ALLOWED_EXTENSIONS_EXCEL'):
		flash('文件名或格式错误，请使用英文名称且不要带"."符号。','danger')
		return redirect(url_for('.stock'))
	dataetime = dt.datetime.today().strftime('%Y%m%d')
	file_dir = 'store/stock/excel/%s/%s/'%(current_user.id,dataetime)
	if not os.path.isdir(current_app.config['UPLOADED_PATH']+file_dir):
		os.makedirs(current_app.config['UPLOADED_PATH']+file_dir)
	
	f.save(current_app.config['UPLOADED_PATH'] +file_dir+filename)
		
	data = xlrd.open_workbook(current_app.config['UPLOADED_PATH'] +file_dir+filename,encoding_override='utf-8')
		
	table=data.sheets()[0]
	message = '' 
	try:
		if table.col(0)[0].value.strip() != '商品编号':
			message = u"第一行名称必须叫‘商品编号’，请返回修改"
		if table.col(1)[0].value.strip() != '货位编号':
			message = u"第二行名称必须叫‘货位编号’，请返回修改"
		if table.col(2)[0].value.strip() != '数量':
			message = u"第三行名称必须叫‘数量’，请返回修改"
		if table.col(3)[0].value.strip() != '备注':
			message = u"第四行名称必须叫‘备注’，请返回修改"

		if message !="":
			flash(message)
			return redirect(url_for('.stock'))
	except e:
		flash('excel文件操作错误：%s'%str(e))
		return redirect(url_for('.stock'))
	
	nrows = table.nrows #行数

	#这里得到表单的数据  商品id 货位id 
	data_list =[ table.row_values(i) for i in range(1,nrows) if table.row_values(i)]

	#获得库存中的商品
	inventory = Inventory.query.filter_by(users=current_user).all()
	inventory_dic = defaultdict(list)
	for i in inventory:
		inventory_dic[str(i.goods_id)+'_'+str(i.goods_allocation_id)].append(i)

	#获取用户货位
	goodsed_allocation = GoodsAllocation.query.filter_by(users=current_user).all()
	goodsed_allocation_dic = defaultdict(list)
	for i in goodsed_allocation:
		goodsed_allocation_dic[str(i.id)].append(i)

	#用户的商品信息
	goodsed = Goods.query.filter_by(seller=current_user.seller_id[0]).all()
	goodsed_dic = defaultdict(list)
	for i in goodsed:
		goodsed_dic[str(i.id)].append(i)


	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	str_time =  time.time()
	number_str = 'S'
	number_str += str(int(int(str_time)*1.301))
	for i in range(2):
		number_str += random.choice(choice_str)

	receipt = Receipt()
	receipt.supplier = form.supplier.data
	receipt.seller = current_user.seller_id[0]
	if form.buy_time.data:
		receipt.buy_time = form.buy_time.data
	if form.send_time.data:
		receipt.send_time = form.send_time.data

	receipt.freight = form.freight.data
	receipt.discount = form.discount.data
	receipt.pay_price = form.pay_price.data

	if form.pay_time.data:
		receipt.pay_time = form.pay_time.data

	receipt.pay_type = form.pay_type.data
	receipt.note = form.note.data
	receipt.number = number_str
	receipt.users = current_user
	receipt.order_state = 1

	"""
		1.检查货位,如果不是该用户货位退出
		2.检查商品,如果不是该用户货位退出
		3.检查是否同库位,同商品,如同则更新,否则添加。

	"""

	#检查商品和货位重复的列
	data_list_dic = {}
	for i in data_list:
		goods_id = str(int(i[0]))
		goods_allocation_id = str(int(i[1]))
		if data_list_dic.has_key(goods_id+'_'+goods_allocation_id):
			count = data_list_dic[goods_id+'_'+goods_allocation_id][2]
			data_list_dic[goods_id+'_'+goods_allocation_id] = [i[0],i[1],i[2]+count,i[3]]
		else:
			data_list_dic[goods_id+'_'+goods_allocation_id] = i
	ast_data_list = []
	for x,y in data_list_dic.iteritems():
		ast_data_list.append(y)

	variety = 0 
	goods_sum = 0
	price_sum = 0

	#表格数据
	for i  in ast_data_list:

		#商品总类
		variety += 1
		#商品总数
		goods_sum += int(i[2])

		success_goodsed = ''
		success_alllocation = ''

		#商品数据
		if goodsed_dic.has_key(str(int(i[0]))):
			success_goodsed = goodsed_dic[str(int(i[0]))][0]
		
		#商品总价
		price_sum += success_goodsed.special_price*int(i[2])

		#货位数据
		if goodsed_allocation_dic.has_key(str(int(i[1]))):
			success_alllocation = goodsed_allocation_dic[str(int(i[1]))][0]
		
		#
		if not success_goodsed:
			flash('商品编号%d校验失败'%i[0])
			abort(401)
		else:
			flash('商品%s校验ok'%(success_goodsed.id))
		#
		if not success_alllocation:
			flash('货位编号%d校验失败'%i[1])
			abort(401)
		else:
			flash('货位%s校验ok'%(success_alllocation.id))

		inventory_dic_has_key = inventory_dic.has_key(str(success_goodsed.id)+'_'+str(success_alllocation.id))
		
		save_stock = Stock()
		save_stock.users = current_user
		save_stock.goodsed = success_goodsed
		save_stock.goods_allocation = success_alllocation
		save_stock.receipts = receipt
		save_stock.stock_count = int(i[2])

		if inventory_dic_has_key:

			count = inventory_dic[str(success_goodsed.id)+'_'+str(success_alllocation.id)][0].count+int(i[2])
			
			save_stock.residue_count = inventory_dic[str(success_goodsed.id)+'_'+str(success_alllocation.id)][0].count

			inventory_dic[str(success_goodsed.id)+'_'+str(success_alllocation.id)][0].update(count=count)
	
			
		else:

			save_stock.residue_count = 0
			
			db.session.add(
				Inventory(
					goodsed = success_goodsed,
					goods_allocation = success_alllocation,
					count = int(i[2]),
					note = i[3],
					users = current_user,
				)
			)
			# print '添加库存：商品信息{success_goodsed.id}，货位{success_alllocation.id}'
		
		db.session.add(save_stock)

	receipt.variety = variety
	receipt.goods_sum = goods_sum
	receipt.price_sum = price_sum

	db.session.add(receipt)

	try:
		db.session.commit()	
		flash('====添加完成=====')
	except e:
		flash('====添加失败=====')
		db.session.rollback()


	return redirect(url_for('.stock'))


#不带表格添加入库单 然后在添加商品完成入库单
@blueprint.route('/add_stock',methods=['POST'])
@login_required
def add_stock():
	form=StockForm()
	if not form.validate_on_submit():
		flash('添加失败','danger')
		flash_errors(form)
		return redirect(url_for('.stock'))

	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	str_time =  time.time()
	number_str = 'S'
	number_str += str(int(int(str_time)*1.301))
	for i in range(2):
		number_str += random.choice(choice_str)

	receipt = Receipt()
	receipt.supplier = form.supplier.data
	receipt.seller = current_user.seller_id[0]
	if form.buy_time.data:
		receipt.buy_time = form.buy_time.data
	if form.send_time.data:
		receipt.send_time = form.send_time.data

	receipt.freight = form.freight.data
	receipt.discount = form.discount.data
	receipt.pay_price = form.pay_price.data

	if form.pay_time.data:
		receipt.pay_time = form.pay_time.data

	receipt.pay_type = form.pay_type.data
	receipt.note = form.note.data
	receipt.number = number_str
	receipt.users = current_user
	receipt.order_state = 0

	receipt.variety = 0
	receipt.goods_sum = 0
	receipt.price_sum = 0

	db.session.add(receipt)
	try:
		db.session.commit()
		return redirect(url_for('.show_receipt',id=receipt.id))
	except e:
		db.session.rollback()
		flash('添加失败。数据错误.')
		return redirect(url_for('.stock'))


#进货单添加商品
@blueprint.route('/receipt_add_goods/<int:id>')
@templated()
@login_required
def receipt_add_goods(id=0):
	return dict(id=id)


@blueprint.route('/receipt_add_goods/<int:id>',methods=['POST'])
@templated()
@login_required
def receipt_add_goods_post(id=0):
	receipt_id = request.form.get('receipt_id')
	goods_name = request.form.get('goods_name')
	allocation_name = request.form.get('allocation_name')
	count = int(request.form.get('count'))
	note = request.form.get('note')

	#入库单信息
	receipt = Receipt.query.get_or_404(id)
	if receipt.users !=current_user:
		abort(404)
	
	#商品信息
	success_goodsed = Goods.query.filter_by(seller=current_user.seller_id[0]).filter_by(title=goods_name).first()
	#货位信息
	success_alllocation = GoodsAllocation.query.filter_by(users=current_user).filter_by(name=allocation_name).first()

	if not success_goodsed:
		flash('信息错误。，没有这个商品，请检查名称是否输入正确')
		return redirect(url_for('.show_receipt',id=id))
	if not success_alllocation:
		flash('信息错误。，没有这个货位，请检查名称是否输入正确')
		return redirect(url_for('.show_receipt',id=id))

	receipt.variety += 1
	receipt.goods_sum += count
	receipt.price_sum += success_goodsed.special_price*count

	#进货商品信息
	save_stock = Stock()
	save_stock.users = current_user
	save_stock.goodsed = success_goodsed
	save_stock.goods_allocation = success_alllocation
	save_stock.receipts = receipt
	save_stock.stock_count = count
	save_stock.users = current_user

	#库存
	inventory = Inventory.query\
		.filter_by(users=current_user)\
		.filter_by(goodsed=success_goodsed)\
		.filter_by(goods_allocation=success_alllocation)\
		.first()
	if inventory:
		inventory.count += count
		save_stock.residue_count = inventory.count
	else:
		db.session.add(
			Inventory(
				goodsed=success_goodsed,
				goods_allocation=success_alllocation,
				users=current_user,
				count=count,
				note=note
				)
			)
		save_stock.residue_count = 0


	db.session.add(save_stock)

	try:
		db.session.commit()
		return redirect(url_for('.show_receipt',id=id))
	except e:
		db.session.rollback()
		flash('添加失败。')
		return redirect(url_for('.show_receipt',id=id))

#完成订单
@blueprint.route('/receipt_change/<int:id>')
@templated()
@login_required
def receipt_change(id=0):
	receipt = Receipt.query.get_or_404(id)
	if receipt.users !=current_user:
		abort(404)
	if receipt.order_state==0:
		receipt.update(order_state=1)
		flash('已完成订单。')


	return redirect(url_for('.show_receipt',id=id))


#进货单模板导出
@blueprint.route('/toexcel_stock_template')
@login_required
def toexcel_stock_template():
    goods_allocation = GoodsAllocation.query.filter_by(users=current_user).order_by('sort').all()
    column_names = ['商品编号','货位编号','数量','备注']

    try:
        response = Response()
        response.status_code = 200

        output = io.StringIO()

        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('sheet')

        for i,x in enumerate(column_names):
        	worksheet.write(0,i,x)
        
        workbook.close()
        output.seek(0)
        response.data = output.read()

        file_name = 'toexcel_stock_template.xlsx'
        mimetype_tuple = mimetypes.guess_type(file_name)

        response_headers = Headers({
                'Pragma': "public",  # required,
                'Expires': '0',
                'Charset': 'UTF-8',
                'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
                'Cache-Control': 'private',  # required for certain browsers,
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'Content-Disposition': 'attachment; filename=\"%s\";' % file_name,
                'Content-Transfer-Encoding': 'binary',
                'Content-Length': len(response.data)
            })

        if not mimetype_tuple[1] is None:
            response.update({
                    'Content-Encoding': mimetype_tuple[1]
                })

        response.headers = response_headers
        response.set_cookie('fileDownload', 'true', path='/')
        return response

    except Exception as e:
        return str(e)


#进货单商品详细
@blueprint.route('/stock_goods/<int:id>')
@templated()
@login_required
def stock_goods(id=0):
	stock = Stock.query.filter_by(receipts_id=id).filter_by(users=current_user).all()
	return dict(stock=stock)


#库存
@blueprint.route('/inventory')
@templated()
@login_required
def inventory(id=0):
	kucun = Inventory.query.filter_by(users=current_user).order_by('count').all()
	return dict(kucun=kucun)


#关注我的
@blueprint.route('/follow')
@templated()
@login_required
def follow(id=0):
	guanzhu = Follow.query.filter_by(seller=current_user.seller_id[0]).all()
	return dict(guanzhu=guanzhu)


#关注店铺
@blueprint.route('/guanzhu/<int:id>')
@templated()
@login_required
def guanzhu(id=0):
	seller = Seller.query.get_or_404(id)
	if seller.users ==  current_user:
		flash('您不能关注自己')
		abort(401)

	if not Follow.query.filter_by(users=current_user).filter_by(seller=seller).first():
		Follow.create(
			users = current_user,
			seller = seller
		)
		flash('您已成功关注该店铺')

	return redirect(url_for('public.home'))


#出售记录
@blueprint.route('/sell')
@templated()
@login_required
def sell(id=0):
	buy_users = UserOrder.query.filter_by(seller=current_user.seller_id[0]).all()
	return dict(buy_users=buy_users)


#显示进货单
@blueprint.route('/show_stock')
@templated()
@login_required
def show_stock():
	all_stock = Receipt.query.filter_by(users=current_user).order_by(desc(Receipt.id)).all()

	return dict(all_stock=all_stock)


#显示进货单详情
@blueprint.route('/show_receipt/<int:id>')
@templated()
@login_required
def show_receipt(id=0):
	receipt = Receipt.query.get_or_404(id)
	if  receipt.users != current_user:
		abort(404)
	return dict(receipt=receipt)


#显示销售单详情
@blueprint.route('/show_order/<int:id>')
@templated()
@login_required
def show_order(id=0):
	user_order = UserOrder.query.get_or_404(id)
	if  user_order.seller != current_user.seller_id[0]:
		abort(404)

	#未查看微信通知
	if not user_order.is_see:
		user_order.update(is_see=True)

	return dict(order=user_order)


#订单拒绝送货 微信通知
@blueprint.route('/order_reject/<int:id>')
@templated()
@login_required
def order_reject(id=0):

	user_order = UserOrder.query.get_or_404(id)
	if  user_order.seller != current_user.seller_id[0]:
		abort(404)

	if user_order.order_state==0:
		flash('订单已拒绝送货')
		user_order.update(order_state=3)

	return redirect(url_for('.show_order',id=id))



#订单开始送货 微信通知
@blueprint.route('/order_confirm/<int:id>')
@templated()
@login_required
def order_confirm(id=0):

	user_order = UserOrder.query.get_or_404(id)
	if  user_order.seller != current_user.seller_id[0]:
		abort(404)

	if user_order.order_state==0:
		flash('订单已开始送货')
		user_order.update(order_state=1)

	return redirect(url_for('.show_order',id=id))





