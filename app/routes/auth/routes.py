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
						 login_required,
						 logout_user)

@auth.route("/logout", methods=['GET'])
def logout():
	if worker.is_authenticated:
		worker.logout()
	if request.device.credential:
		return redirect(url_for('auth.passkey', token='await'))
	return redirect(url_for('auth.password'))