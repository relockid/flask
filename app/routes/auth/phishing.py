import bleach

from . import _ as auth, logging
from flask import (current_app as app,
				   render_template,
				   request,
				   redirect,
				   url_for,
				   flash,
				   abort)
from flask_login import (current_user as worker,
						 login_required)

from ...models.user import User

@auth.route('/phishing', methods=['GET', 'POST'])
def phishing(email=None, passwd=None, user=None, error=list()):
	return render_template('phishing.html', error=error,
										    email=email,
										    passwd=passwd)
