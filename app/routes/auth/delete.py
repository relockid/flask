import bleach
import binascii
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
from ... import db


@auth.route("/delete/<string:token>", methods=['GET'])
@auth.route("/delete", methods=['GET'])
@login_required
def delete(token=None, 
		   email=None, 
		   user=None, 
		   credential=None, 
		   error=list()):
	error.clear();

	if request.method == 'GET' and request.device.owner:
		if user := User.query.filter_by(id=int(request.device.owner)).first():
			email = user.email
			session['email'] = email = user.email
			session['identity'] = user.get_id()
	elif user := User.query.filter_by(id=session.get('identity')).first():
		session['email'] = email = user.email
		session['identity'] = user.get_id()
	
	if not 'identity' in session or not user:
		return abort(401)

	if not 'token' in session:
		session['token'] = binascii.hexlify(os.urandom(16)).decode()

	""" Re-authentication of the user and if successfull 
		remove the passkey from the system. The process of 
		re-authentication is invoked by the javascript on the 
		browser side.
	"""
	if request.device.credential:
		if request.device.passkey and user:
			db.session.delete(user)
			db.session.commit()
			session.pop('token')
			del request.device.credential
			return redirect(url_for('auth.clear'))
	elif token == session.get('token') and user:
		db.session.delete(user)
		db.session.commit()
		session.pop('token')
		return redirect(url_for('auth.clear'))
	return render_template('delete.html', error=error,
										  email=email,
										  token=session.get('token'),
										  credential=request.device.credential)
