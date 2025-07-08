from flask import current_app as app, session, request, Response, redirect, url_for, abort, render_template, flash
from flask_login import current_user as worker, login_user, logout_user, login_required

from ...models.company import Company
from ...models.user import User
from ... import db

from uuid import uuid4

from . import _ as bp, logging

import bleach
import hashlib

_ = Response('Bad Request', status=500, content_type='text/html; charset=utf-8')

app.config.TRACE_CACHE = True

@bp.route("/index", methods=['GET'])
@login_required
def index():
    if not worker.key:
        worker.key = hashlib.blake2b(worker.email.encode(),
                                   salt=worker.get_id().to_bytes(16, byteorder='big'),
                                   digest_size=16).hexdigest()
        worker.update()
        db.session.commit()

    return render_template('index_explore.html', key=worker.key)
