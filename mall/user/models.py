# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin

from mall.database import Column, Model, SurrogatePK, db, reference_col, relationship
from mall.extensions import bcrypt



#权限常量
class Permission:
    ADMINISTER = 0x8000  #管理员权限


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)

    user = relationship('User', backref='roles')
    
    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)

    @staticmethod
    def insert_roles():
        roles = {
            'User':(0,True),
            'ADMIN': (0xffff, False) #管理员
        }
        for r in roles:
            print(r)
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = 'users'
    username = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    password = Column(db.Binary(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)

    #位置
    address_map =  Column(db.String(100)) 
    #手机号，也可以用于登陆
    phone  = Column(db.String(20),index=True,unique=True) 
    #最后一次登陆时间
    last_time = Column(db.DateTime,default=dt.datetime.now) 

    wechat_id = Column(db.String(100)) 

    role_id = reference_col('roles', nullable=True)
    


    
    #店铺一对一
    seller_id = relationship('Seller', backref='users',uselist='False',lazy='select')
    #用户收货地址
    user_address_id = relationship('UserAddress', backref='users')
    #订单
    user_order_id = relationship('UserOrder', backref='users_buy')
    #货位
    goods_allocation_id = relationship('GoodsAllocation', backref='users')
    #库存
    inventory_id = relationship('Inventory', backref='users')
    #进货单
    receipt_id = relationship('Receipt', backref='users')
    stock_id = relationship('Stock', backref='users')
    buys_car_id = relationship('BuysCar', backref='users')
    follows_id = relationship('Follow', backref='users')
    #盘点表
    quantity_check_id = relationship('QuantityCheck', backref='users')
    

    
    
    

    def __init__(self, username, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        """Full user name."""
        return '{0} {1}'.format(self.first_name, self.last_name)

    def can(self, permissions):
        return self.roles is not None and \
            (self.roles.permissions & permissions) == permissions

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)

    def can(self, permissions):
        return self.roles is not None and \
            (self.roles.permissions & permissions) == permissions




