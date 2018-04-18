# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
from flask import flash, request, render_template, current_app
from functools import wraps

from PIL import Image
import PIL,os,time,random,hashlib



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



def allowed_file(filename,config_name):
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
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)

        if not os.path.isdir(current_app.config['THUMBNAIL_FOLDER']+file_dir):
            os.makedirs(current_app.config['THUMBNAIL_FOLDER']+file_dir)
        img.save(os.path.join(current_app.config['THUMBNAIL_FOLDER'], file_dir+filename))
        
        return True
    except:
        return False




