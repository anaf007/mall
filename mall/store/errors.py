from .import blueprint
from mall.utils import templated

@blueprint.app_errorhandler(404)
@templated('404.html')
def page_not_found(e):
    return dict()

@blueprint.app_errorhandler(500)
@templated('500.html')
def internal_server_error(e):
    return dict()

@blueprint.app_errorhandler(403)
@templated('403.html')
def page_403(e):
    return dict()

@blueprint.app_errorhandler(401)
@templated('/stroe/401.html')
def page_401(e):
    print('===')
    return dict()