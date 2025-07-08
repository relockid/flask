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

@auth.route('/unrecognised', methods=['GET', 'POST'])
def unrecognised(error=list()):
	if not request.device.confirm():
		return render_template('unrecognised.html', error=error,
										    		email=email)
	return redirect(url_for('auth.identity'))
