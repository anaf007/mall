# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin

from mall.database import Column, Model, SurrogatePK, db, reference_col, relationship
from mall.extensions import bcrypt


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col('users', nullable=True)
    
    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)


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


    role = relationship('Role', backref='roles')
    seller_id = relationship('Seller', backref='users')
    user_address_id = relationship('UserAddress', backref='users')
    user_order_id = relationship('UserOrder', backref='users_buy')
    # car_session_id = relationship('CarSession', backref='users')

    
    
    

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

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)




