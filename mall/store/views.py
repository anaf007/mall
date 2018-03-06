#coding=utf-8
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import desc
from mall.utils import templated
from flask_login import login_required

blueprint = Blueprint('store', __name__, url_prefix='/store')


@blueprint.route('/')

@templated('store/home.html')
@login_required
def home():
    return dict()

