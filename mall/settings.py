# -*- coding: utf-8 -*-
"""Application configuration."""
import os


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('MALL_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #ckeditor config
    CKEDITOR_WIDTH = 500
    CKEDITOR_HEIGHT = 300

    ALLOWED_EXTENSIONS_EXCEL = set(['xlsx'])

    UPLOADED_PATH = 'data/uploads/'
    

    #取消sql自动提交 
    SQLALCHEMY_COMMIT_ON_TEARDOWN =  False

    #图片上传
    THUMBNAIL_FOLDER = 'data/uploads/thumbnail/'
    ALLOWED_EXTENSIONS_IMAGES = set(['png', 'jpg', 'jpeg', 'gif'])

    #最大上传文件大小
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # 2MB

    MALL_WECHAT_TOKEN = ''

    #测试号
    # WECHAT_TYPE = 0 #0  订阅号   服务号
    WECHAT_APPID = os.environ.get('MALL_WECHAT_APPID') or 'wxb27de34ba5055b6b'
    WECHAT_SECRET = os.environ.get('MALL_WECHAT_SECRET') or '1ea339c37b7e356def3d9aea0da65d85'
    WECHAT_TOKEN = os.environ.get('MALL_WECHAT_TOKEN') or 'wx_get_token_1234567890acb'
    # WECHAT_APPID =  'wxb27de34ba5055b6b'
    # WECHAT_SECRET =  '1ea339c37b7e356def3d9aea0da65d85'
    # WECHAT_TOKEN =  'wx_get_token_1234567890acb'


    #ckeditor config
    #ckeditor 图片上传地址url
    #ckeditor服务器上传函数
    CKEDITOR_FILE_UPLOADER = '/upload'
    #上传存放路径
    CKEDITOR_FILE_UPLOAD_URL =  'data/ckeditor/uploads/'

    # CKEDITOR_FILE_BROWSER_URL = 'data/ckeditor/uploads/'

    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '123'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '123'
    MAIL_RECIPIENTS_NAME = os.environ.get('MAIL_RECIPIENTS_NAME') or '123'  
    MAIL_DEBUG = False

    SUPERADMIN_NAME = 'admin'

     


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('prod_mall_database_url') or \
        'mysql://root:@127.0.0.1:3306/mall'
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    SQLALCHEMY_DATABASE_URI = os.environ.get('prod_mall_database_url') or \
        'mysql://root:@127.0.0.1:3306/mall'
    DEBUG_TB_ENABLED = True
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing
