from flask import current_app as app, session, request, Response, redirect, url_for, abort, render_template, flash
from flask_login import current_user as worker, login_user, logout_user, login_required

from ...models.company import Company
from ...models.user import User

from uuid import uuid4

from . import _ as bp, logging

import random

_ = Response('Bad Request', status=500, content_type='text/html; charset=utf-8')

app.config.TRACE_CACHE = True

@bp.route("/", methods=['GET'])
@login_required
def index():
    return render_template('index.html')


@bp.route("/test", methods=['GET'])
@login_required
def test():
    return render_template('test.html')