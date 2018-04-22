# -*- coding: utf-8 -*-
"""The store module, including the homepage and user auth."""
from flask import Blueprint

blueprint = Blueprint('store', __name__, url_prefix='/store')

from . import views, models,views_json  # noqa
