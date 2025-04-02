import bleach

from datetime import datetime

from . import _ as auth, logging
from flask import (current_app as app,
				   render_template,
				   request,
				   redirect,
				   session,
				   url_for,
				   flash,
				   abort)
from flask_login import (current_user as worker,
						 login_required)

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

@auth.route("/password/<string:token>", methods=['GET', 'POST'])
@auth.route('/password', methods=['GET', 'POST'])
def password(token=None, email=None, passwd=None, user=None, error=list()):
	error.clear()
	if 'identity' in session:
		if user := User.query.filter_by(id=int(session.get('identity'))).first():
			session['email'] = email = user.email
		else:
			return redirect(url_for('auth.identity'))

	if request.device.owner:
		if user := User.query.filter_by(id=request.device.owner).first():
			email = user.email; session['identity'] = user.get_id()
		else:
			error.append('user')
	if request.method == 'POST' and request.form.get('password'):
		if request.device.confirm():
			passwd = bleach.clean(request.form.get('password'))
		else:
			return abort(403)
		if passwd and not schema.validate(passwd):
			error.append('passwd')
		if not error and passwd and user:
			if user.check_password(passwd) and user.login():
				if token is not None:
					return redirect(url_for('auth.passkey'))
				if 'identity' in session:
					session.pop('identity')
				return redirect(url_for('index.index'))
			else:
				error.append('invalid')
	return render_template('password.html', error=error,
										    email=email,
										    token=token,
										    passwd=passwd)
