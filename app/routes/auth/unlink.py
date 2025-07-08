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


@auth.route("/unlink", methods=['GET'])
@login_required
def unlink(email=None, 
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
	
	if not request.device.owner:
		return abort(401)
	return render_template('unlink.html', error=error,
										  email=email,
										  credential=request.device.credential)
