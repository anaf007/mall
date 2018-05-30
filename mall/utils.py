# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
from flask import flash, request, render_template, current_app
from functools import wraps
from flask_mail import Message

from PIL import Image
import os,random,random

import datetime as dt

#生成无重复随机数
gen_rnd_filename = lambda :"%s%s" %(dt.datetime.now().strftime('%Y%m%d%H%M%S'), str(random.randrange(1000, 10000)))
#文件名合法性验证
allowed_file_lambda = lambda filename: '.' in filename and filename.rsplit('.', 1)[1] in set(['txt', 'xls', 'xlsx', 'gif', 'bmp'])



def flash_errors(form, category='warning'):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash('{0} - {1}'.format(getattr(form, field).label.text, error), category)


def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                    .replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator



def allowed_file(filename,config_name='ALLOWED_EXTENSIONS_IMAGES'):
    if '.' in filename and \
        filename.rsplit('.', 1)[1] in current_app.config['{}'.format(config_name)] :
        return True
    else:
        return False



def create_thumbnail(f,base_width,file_dir,filename):
    try:
        base_width = base_width
        thumbnail_f = f
        img = Image.open(thumbnail_f)
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), Image.ANTIALIAS)

        if not os.path.isdir(current_app.config['THUMBNAIL_FOLDER']+file_dir):
            os.makedirs(current_app.config['THUMBNAIL_FOLDER']+file_dir)
        img.save(os.path.join(current_app.config['THUMBNAIL_FOLDER'], file_dir+filename))
        
        return True
    except:
        return False


def send_email(body):
    msg = Message(subject='公众号隔壁小超市错误邮件提醒%s'%dt.datetime.now().strftime('%Y%m%d%H%M%S'),sender=current_app.config['MAIL_USERNAME'],recipients=[current_app.config['MAIL_RECIPIENTS_NAME']])
    msg.html = body
    mail.send(msg)



