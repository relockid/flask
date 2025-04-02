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

from email_validator import (validate_email, 
							 EmailNotValidError)

from password_validator import PasswordValidator

# Create a schema
# .has().uppercase() \
# .has().symbols() \
schema = PasswordValidator()
schema \
.min(8) \
.max(100) \
.has().lowercase() \
.has().digits() \
.has().no().spaces()

from ...models.user import User
from ...plugins.mail import Mail

@app.route('/reset/<string:token>', methods=['GET', 'POST'])
def reset(token=None, user=None, email=None, error=list()):
	error.clear()
	if request.method == 'GET' and token is not None \
							   and request.device.validate(token):
		if user := User.query.filter_by(id=session.get('identity', int())).first():
			email = user.email
	if request.method == 'POST' and request.device.confirm():
		if passwd := bleach.clean(request.form.get('password', str())):
			if not schema.validate(passwd):
				error.append('passwd')
			if user := User.query.filter_by(id=session.get('identity')).first():
				if not error and passwd:
					if user.change_password(passwd):
						return redirect(url_for('auth.password'))
			else:
				error.append('invalid')
		else:
			error.append('passwd')
	return render_template('reset.html', error=error,
										 email=email)

@auth.route("/forgot", methods=['GET', 'POST'])
def forgot(email=None, user=None, error=list()):
	error.clear()
	if request.method == 'POST' and request.form.get('email'):
		if request.device.confirm():
			email = bleach.clean(request.form.get('email'))
		else:
			# if user press Ctrl+R this may cause this event
			# as tokens may be used only once
			pass
		try:
			if email is not None:
				emailinfo = validate_email(email, check_deliverability=False)
				email = emailinfo.normalized
		except EmailNotValidError as e:
			error.append('email');
		else:
			if email is not None:
				if user := User.query.filter_by(email=email).first():
					session['email'] = user.email
					session['identity'] = user.get_id()
				else:
					error.append('user')
		finally:
			if not error and user:
				url = url_for('reset', token=request.device.token())
				url = app.config.get('SERVER_HSTS') + '://' \
					  + app.config.get('SERVER_HOST') + url
				m = Mail('forgot') \
					 .subject('New password requested') \
					 .text(user=email, link=url, host=app.config.get('SERVER_HOST')) \
					 .html(user=email, link=url, host=app.config.get('SERVER_HOST')) \
					 .to(email)
				m.send(threading=True)
				error.append('send')
				# session.pop('identity')
	if request.method == 'GET' and request.device.owner:
		if user := User.query.filter_by(id=int(request.device.owner)).first():
			email = user.email
			session['email'] = user.email
			session['identity'] = user.get_id()
	return render_template('forgot.html', error=error,
										  email=email)
