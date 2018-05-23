from functools import wraps
from flask import abort,flash
from flask_login import current_user
from mall.user.models  import Permission


def permission_required(permission):
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                flash('您没有权限访问。')
                abort(401)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
