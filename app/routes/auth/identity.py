import bleach

from . import _ as auth, logging

from flask import (current_app as app,
				   render_template,
				   session,
				   request,
				   redirect,
				   url_for,
				   flash,
				   abort)

from email_validator import (validate_email, 
							 EmailNotValidError)

from ...models.user import User

@auth.route('/identity', methods=['GET', 'POST'])
def identity(email=None, passwd=None, user=None, error=list()):
	if request.method == 'POST' and request.form.get('email'):
		if email := bleach.clean(request.form.get('email')):
			if not request.device.confirm(reuse=True):
				logging.error('Unconfirmed request.')
			try:
				error.clear()
				if email is not None:
					emailinfo = validate_email(email, check_deliverability=False)
					email = emailinfo.normalized
			except EmailNotValidError as e:
				error.append('email');
			else:
				if email is not None:
					if user := User.query.filter_by(email=email).first():
						session['identity'] = user.get_id()
						session['email'] = user.email
					else:
						error.append('user')
				else:
					raise ValueError('Invalid email.')
			finally:
				if not error and user and email:
					if request.device.credential:
						return redirect(url_for('auth.passkey'))
					if request.device.owner == user.get_id():
						return redirect(url_for('auth.password'))
					if request.device.protected:
						return redirect(url_for('auth.forbidden'))
					return redirect(url_for('auth.approve'))
	return render_template('identity.html', error=error,
										    email=email)
