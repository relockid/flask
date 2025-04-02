import bleach

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

@app.route('/ticket/<string:token>', methods=['GET'])
def ticket(token=bytes(), error=list()):
	if token and request.device.validate(token):
		if 'identity' in session:
			if user := User.query.filter_by(id=session.get('identity')).first():
				session['identity'] = user.get_id()
				session['email'] = user.email
				if request.device.credential:
					return redirect(url_for('auth.passkey'))
				return redirect(url_for('auth.password'))
	return redirect(url_for('auth.phishing'))

@auth.route("/approve", methods=['GET', 'POST'])
def approve(user=None, email=None, error=list()):
	error.clear();
	if 'identity' in session:
		if user := User.query.filter_by(id=session.get('identity')).first():
			session['email'] = email = user.email
			session['identity'] = user.get_id()
		else:
			error.clear(); error.append('user')
		if not error and user:
			if token := request.device.token():
				url = url_for('ticket', token=token)
				url = app.config.get('SERVER_HSTS') + '://' \
					  + app.config.get('SERVER_HOST') + url
				print(url)
				m = Mail('authorisation') \
					 .subject('Device authorisation requested') \
					 .text(user=user.email, link=url, host=app.config.get('SERVER_HOST')) \
					 .html(user=user.email, link=url, host=app.config.get('SERVER_HOST')) \
					 .to(user.email)
				m.send(threading=True)
				error.append('send')
	else:
		error.append('identity')
	return render_template('approve.html', error=error)
