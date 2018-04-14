# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
from flask import flash, request, render_template, current_app
from functools import wraps



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


