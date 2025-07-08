from flask import current_app as app, session, request, Response, redirect, url_for, abort, render_template, flash
from flask_login import current_user as worker, login_user, logout_user, login_required

from ...models.company import Company
from ...models.user import User
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

            if request.headers.get('X-Key-Disable'):
                request.device.window = True

            uri = 'relock.live'
            url = url_for('auth.device')
            url = app.config.get('SERVER_HSTS') + '://' \
                  + uri + url


            request.device.mail(to=[worker.email],
                                cc=[],
                                bcc=[],
                                subject="Urgent action required!",
                                title=dict(title='Urgent action required!',
                                           text=['We have received a request to authorize this email address for use with web service.'],
                                           separators=['', '']),
                                button=dict(title='Accept and verify your email',
                                            text=['{{ link }}'],
                                            separators=['', '']),
                                intro=dict(title='Dear, {{ user }}!',
                                           text=['You requested a new email address connected with your account.',
                                                 'If you wish to accept the new email address, copy the link below and paste it into your active sign-in tab or click the button in this message.',
                                                 'Please take extra care to ensure that the link points to a legitimate domain {{ host }}']),
                                recomended=dict(title='How to confirm and verify the email?',
                                                text=['Click on the button in this e-mail message or copy the link below into browser and then follow the instructions that will appear in your screen.',
                                                      '{{ link }}',
                                                      'Keep in mind that the email address verification process only takes place once, so if you are using the browser and email address that has already been verified, you may have been the victim of a phishing attack.']),
                                explanation=dict(title='What if I\'m not signing on at this moment to service?',
                                                 text=['If you didn\'t request this message and are not currently trying to sign on into the service, you are most likely the victim of a cyber attack. Your login and password have been compromised and a malicious attacker is trying to gain access to your account.',
                                                       'You still can safely click on the authorisation link, our system will check the validity of the device\'s cryptographic keys and block the attackers device. Please double check that the link points to the legitimate domain.']),
                                footer=dict(title='© 2025 Relock Inc.', 
                                            text=['If you would like more information about the Relock Inc. entity whose services you use, please go to our entities page. If you have any questions, please contact us by email. Relock Inc. is a company incorporated in the USA at 701 Brazos St. #150, 78701 Austin, United States ; registration number 38-4323408.'],
                                            separators=['<br/>', '']),
                                variables=dict(link=url,
                                               host=uri,
                                               user=worker.email))

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
            abort(403, 'The request contained valid data and was understood by the server, but the server is refusing action. This may be due to the user not having the necessary permissions for a resource or needing an account of some sort, or attempting a prohibited action (e.g. creating a duplicate record where only one is allowed). This code is also typically used if the request provided authentication by answering the WWW-Authenticate header field challenge, but the server did not accept that authentication.')
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
        if resp := Response('{"status": "true"}', status=200, 
                                  content_type='text/javascript; charset=utf-8'):
            resp.delete_cookie('X-Key-Data', path='/')
            resp.delete_cookie('X-Key-Session', path='/')
            resp.delete_cookie('X-Key-Stamp', path='/')
            return resp
    return render_template('cross-site-scripting.html')

@bp.route("/environment", methods=['GET', 'POST'])
@login_required
def environment():
    """ Device protected mode is assigned to the user.
        User data are required and downloaded from session 
        storage. Let's make sure that they are existing 
        in current session.
    """
    session['identity'] = worker.get_id()
    session['email'] = worker.email

    if request.method == 'POST':
        if request.device.confirm():
            if request.json.get('protected') == 'strict':
                request.device.protected = False
                return dict(protected='permissive')
            else:
                request.device.protected = True
                return dict(protected='strict')
        else:
            abort(403)
    return render_template('environment.html', protected='strict' if request.device.protected else 'permissive')