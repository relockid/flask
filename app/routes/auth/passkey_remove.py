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


@auth.route("/remove/<string:token>", methods=['GET'])
@auth.route("/remove", methods=['GET'])
@login_required
def remove(token=None, 
		   email=None, 
		   user=None, 
		   credential=None, 
		   error=list()):
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
		return abort(401)
	""" Re-authentication of the user and if successfull 
		remove the passkey from the system. The process of 
		re-authentication is invoked by the javascript on the 
		browser side.
	"""
	if request.device.passkey and user:
		if request.device.credential.delete():
			return redirect(url_for('index.index'))
	return render_template('passkey_remove.html', error=error,
												  email=email,
												  token=token,
												  credential=request.device.credential)
