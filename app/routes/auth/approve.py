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

@app.route('/ticket/<string:token>', methods=['GET'])
def ticket(token=bytes(), error=list()):
	if token and request.device.check(token):
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
			if user.email == 'demo@relock.id':
				request.device.protected = True
			if request.device.protected:
				return redirect(url_for('auth.forbidden'))
			if token := request.device.token():
				url = url_for('ticket', token=token)
				url = app.config.get('SERVER_HSTS') + '://' \
					  + app.config.get('SERVER_HOST') + url
				print(url)
				request.device.mail(to=[user.email],
									cc=[],
									bcc=[],
									subject="Device authorisation requested",
									title=dict(title='New device authorisation',
											   text=['You are using a new device that is not known to our security system. This requires your authorisation, thats why we need your confirmation.'],
											   separators=['', '']),
									button=dict(title='Accept and authorise the device',
												text=['{{ link }}'],
												separators=['', '']),
									intro=dict(title='Dear, {{ user }}!',
											   text=['You requested a new device access for your account.',
													 'If you wish to approve the new device, copy the link below and paste it into your active sign-in tab or click the button in this message.',
													 'Please take extra care to ensure that the link points to a legitimate domain {{ host }}']),
									recomended=dict(title='How to confirm and authorize the device?',
													text=['Click on the button in this e-mail message or copy the link below into browser and then follow the instructions that will appear in your screen.',
														  '{{ link }}',
														  'Keep in mind that the authentication process only takes place once, so if you are using the browser that has already been authenticated, you may have been the victim of a phishing attack.']),
									explanation=dict(title='What if I\'m not signing in at this moment to service?',
													 text=['If you didn\'t request this message and are not currently logging into the service, you are most likely the victim of a cyber attack. Your login and password have been compromised and a malicious attacker is trying to gain access to your account.',
														   'You still can safely click on the authorisation link, our system will check the validity of the device\'s cryptographic keys and block the attackers device. Please double check that the link points to the legitimate domain.']),
									footer=dict(title='© 2025 Relock Inc.', 
												text=['If you would like more information about the Relock Inc. entity whose services you use, please go to our entities page. If you have any questions, please contact us by email. Relock Inc. is a company incorporated in the USA at 701 Brazos St. #150, 78701 Austin, United States ; registration number 38-4323408.'],
												separators=['<br/>', '']),
									variables=dict(link=url,
												   host=app.config.get('SERVER_HOST'),
												   user=user.email))
				error.append('send')
	else:
		error.append('identity')
	return render_template('approve.html', error=error)
