import bleach
import os

from datetime import datetime

from . import _ as auth, logging
from flask import (current_app as app,
				   render_template,
				   session,
				   request,
				   redirect,
				   url_for,
				   flash,
				   abort)
from flask_login import (current_user as worker,
						 login_required)

from ...models.user import User
from ...plugins.mail import Mail


@auth.route("/passkey/<string:token>", methods=['GET'])
@auth.route("/passkey", methods=['GET'])
def passkey(token=None, email=None, user=None, credential=None, error=list()):
	error.clear(); token = True if token else False

	if request.method == 'GET' and request.device.owner:
		if user := User.query.filter_by(id=int(request.device.owner)).first():
			email = user.email
			session['email'] = email = user.email
			session['identity'] = user.get_id()
	elif user := User.query.filter_by(id=session.get('identity')).first():
		session['email'] = email = user.email
		session['identity'] = user.get_id()
	
	if not 'identity' in session or not user:
		error.append('user')
	if not request.device.credential:
		error.append('new')
	if _ := session.get('challenge', bytes):
		if session.get('passkey', bytes()) == _ and user:
			if user.login():
				session.pop('passkey')
				session.pop('challenge')
				session.pop('identity')
				return redirect(url_for('index.index'))
	return render_template('passkey.html', error=error,
										   email=email,
										   token=token,
										   credential=request.device.credential)
