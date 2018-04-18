# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_wechatpy import Wechat
from flask_ckeditor import CKEditor

bcrypt = Bcrypt()
csrf_protect = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
ckeditor = CKEditor()
wechat = Wechat()

login_manager.session_protection ='strong'
login_manager.login_view = 'user.autologin'
# login_manager.login_message = "请登录后访问该页面."
login_manager.refresh_view = 'auth.autologin'
