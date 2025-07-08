import bleach

from datetime import datetime

from . import _ as auth, logging
from flask import (current_app as app,
				   render_template,
				   request,
				   session,
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

@auth.route('/signin', methods=['GET', 'POST'])
def signin(email=None, passwd=None, user=None, error=list()):
	error.clear()
	if request.method == 'POST' and request.form.get('email'):
		if request.device.confirm():
			email = bleach.clean(request.form.get('email'))
			passwd = bleach.clean(request.form.get('password'))
		else:
			return abort(403)
		try:
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
					if user.email == 'demo@relock.id':
						request.device.protected = True
				else:
					error.append('user')
		finally:
			if passwd and not schema.validate(passwd):
				error.append('passwd')
			if not error and user and passwd:
				if user.check_password(passwd):
					if request.device.owner == user.get_id():
						user.login()
					else:
						if request.device.has_window(user.get_id()) and user.login():
							return redirect(url_for('index.index'))
						if request.device.protected:
							return redirect(url_for('auth.forbidden'))	
						return redirect(url_for('auth.approve'))
					return redirect(url_for('index.index'))
				else:
					error.append('invalid')
	return render_template('signin.html', error=error,
										  email=email,
										  passwd=passwd)
