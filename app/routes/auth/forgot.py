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

@app.route('/reset/<string:token>', methods=['GET', 'POST'])
def reset(token=None, user=None, email=None, error=list()):
	error.clear()
	if request.method == 'GET' and token is not None \
							   and request.device.check(token):
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

				request.device.mail(to=[user.email],
									cc=[],
									bcc=[],
									subject="New password requested",
									title=dict(title='New password requested',
											   text=['You requested a password change. This requires identity prove, thats why we need your confirmation.'],
											   separators=['', '']),
									button=dict(title='Click to change your password',
										  		text=['{{ link }}'],
										  		separators=['', '']),
									intro=dict(title='Dear, {{ user }}!',
										  	   text=['You requested a new password for your account.',
										  		 	 'If you wish to change the password, copy the link below and paste it into your active sign-in tab or click the button in this message.',
										  		 	 'Please take extra care to ensure that the link points to a legitimate domain {{ host }}']),
									recomended=dict(title='How to confirm a change of password?',
										  			text=['Click on the button in this e-mail message or copy the link below into browser and then follow the instructions that will appear in your screen.',
										  				  '{{ link }}',
										  				  'Keep in mind that the authentication process only takes place once, so if you are using the browser that has already been authenticated, you may have been the victim of a phishing attack.']),
									explanation=dict(title='What if I\'m not requested this email?',
										  			 text=['If you didn\'t request this message and are not currently logging into the service, you are most likely the victim of a cyber attack. Your login have been compromised and a malicious attacker is trying to gain access to your account.',
										  				   'You still can safely click on the authorisation link, our system will check the validity of the device\'s cryptographic keys and block the attackers device. Please double check that the link points to the legitimate domain.']),
									footer=dict(title='© 2025 Relock Inc.', 
												text=['If you would like more information about the Relock Inc. entity whose services you use, please go to our entities page. If you have any questions, please contact us by email. Relock Inc. is a company incorporated in the USA at 701 Brazos St. #150, 78701 Austin, United States ; registration number 38-4323408.'],
												separators=['<br/>', '']),
									variables=dict(link=url,
									  			   host=app.config.get('SERVER_HOST'),
									  			   user=user.email))
				error.append('send')
				# session.pop('identity')
	if request.method == 'GET' and request.device.owner:
		if user := User.query.filter_by(id=int(request.device.owner)).first():
			email = user.email
			session['email'] = user.email
			session['identity'] = user.get_id()
	return render_template('forgot.html', error=error,
										  email=email)
