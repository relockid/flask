from flask import current_app as app, session, request, Response, redirect, url_for, abort, render_template, flash
from flask_login import current_user as worker, login_user, logout_user, login_required

from ...models.company import Company
from ...models.user import User
from ...plugins.mail import Mail
from ... import db

from uuid import uuid4

from . import _ as bp, logging

import bleach
import random

_ = Response('Bad Request', status=500, content_type='text/html; charset=utf-8')

app.config.TRACE_CACHE = True

@bp.route("/index", methods=['GET'])
@login_required
def index():
    return render_template('indexs.html')

@bp.route("/stuffing", methods=['GET'])
@login_required
def stuffing():
    return render_template('stuffing.html')

@bp.route("/hijacking", methods=['GET'])
@login_required
def hijacking():
    return render_template('hijacking.html')

@bp.route("/adversary", methods=['GET', 'POST'])
@login_required
def adversary():
    if request.method == 'POST':
        if request.device.confirm():
            uri = 'relock.live'
            url = url_for('auth.device')
            url = app.config.get('SERVER_HSTS') + '://' \
                  + uri + url
            m = Mail('phishing') \
                 .subject('Urgent action required!') \
                 .text(user=worker.email, link=url, host=uri) \
                 .html(user=worker.email, link=url, host=uri) \
                 .to(worker.email)
            m.send(threading=True)
            return dict(email=worker.email)
        else:
            abort(403)
    return render_template('adversary.html')

@bp.route("/infostealers", methods=['GET'])
@login_required
def infostealers():
    return render_template('infostealers.html')

@bp.route("/credentials", methods=['GET'])
@login_required
def credentials():
    return render_template('credentials.html')

@bp.route("/requests", methods=['GET', 'POST'])
@login_required
def requests(email=None):
    if not email:
        email = worker.email
    if request.method == 'POST':
        if request.device.confirm() and request.form.get('email'):
            email = bleach.clean(request.form.get('email'))
        else:
            abort(403, 'Mallicious requests are not allowed.')
    return render_template('requests.html', email=email)

@bp.route("/reply", methods=['GET', 'POST'])
@login_required
def reply():
    if request.method == 'POST':
        if request.device.confirm():
            return dict(email=worker.email)
        else:
            abort(403)
    return render_template('reply.html')

@bp.route("/session", methods=['GET', 'POST'])
@login_required
def sessions():
    if request.method == 'POST':
        if request.device.confirm():
            return session.get('screens', dict())
        else:
            abort(403)
    return render_template('session.html')

@bp.route("/cross-site-scripting", methods=['GET', 'POST'])
@login_required
def cross_site_scripting():
    if request.method == 'POST':
        if request.device.confirm():
            setattr(request, '__clear_cookie', True)
            return dict(status='OK')
        else:
            abort(403)
    return render_template('cross-site-scripting.html')

@bp.route("/environment", methods=['GET', 'POST'])
@login_required
def environment():
    if request.method == 'POST':
        if request.device.confirm():
            if request.json.get('protected') == 'strict':
                worker.protected=False
                worker.save()
                db.session.commit()
                return dict(protected='permissive')
            else:
                worker.protected=True
                worker.save()
                db.session.commit()
                return dict(protected='strict')
        else:
            abort(403)
    return render_template('environment.html', protected='strict' if worker.protected else 'permissive')