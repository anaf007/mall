# -*- coding: utf-8 -*-
"""The superadmin module, including the homepage and user auth."""

from flask import Blueprint

blueprint = Blueprint('superadmin', __name__, url_prefix='/superadmin')

from . import views, models, views_store  # noqa
