# -*- coding: utf-8 -*-
"""The superadmin module, including the homepage and user auth."""

from flask import Blueprint

blueprint = Blueprint('superadmin', __name__, url_prefix='/superadmin')

from . import models,views, views_store,api  # noqa
