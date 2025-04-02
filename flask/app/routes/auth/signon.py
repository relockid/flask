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

@auth.route('/signon', methods=['GET', 'POST'])
def signon(email=None, passwd=None, user=None, error=list()):
	error.clear()
	if request.method == 'POST' and request.form.get('email'):
		if request.device.confirm():
			email = bleach.clean(request.form.get('email'))
			passwd = bleach.clean(request.form.get('password'))
		else:
			# If user press the Ctrl+R the invalid token should 
			# cause an 401 Unauthorized error at this moment, but 
			# for the comfort of user let's allow to continue.
			pass
		try:
			if email is not None:
				emailinfo = validate_email(email, check_deliverability=False)
				email = emailinfo.normalized
		except EmailNotValidError as e:
			error.append('email');
		else:
			if user := User.query.filter_by(email=email).first():
				error.append('user')
		finally:
			if passwd and not schema.validate(passwd):
				error.append('passwd')
			if not error and not user and email and passwd:
				if user := User(email=email,
								password=passwd):
					session['identity'] = user.get_id()
					session['email'] = user.email
					if not user.veryficated:
						return redirect(url_for('auth.verify'))
					if user.login():
						return redirect(url_for('index.index'))
	return render_template('signup.html', error=error,
										  email=email,
										  passwd=passwd)
