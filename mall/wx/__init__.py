# -*- coding: utf-8 -*-
"""The user module."""

from flask import Blueprint

blueprint = Blueprint('wx', __name__, url_prefix='/wx')

from . import token  