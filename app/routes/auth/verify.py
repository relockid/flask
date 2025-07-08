import bleach
import hashlib

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
from ... import db

@app.route('/confirm/<string:token>', methods=['GET'])
def confirm(token=bytes(), error=list()):
	if token and request.device.check(token):
		if 'identity' in session:
			if user := User.query.filter_by(id=session.get('identity')).first():
				session['identity'] = user.get_id()
				session['email'] = user.email

				user.key = hashlib.blake2b(user.email.encode(),
				                		   salt=user.get_id().to_bytes(16, byteorder='big'),
				                		   digest_size=16).hexdigest()
				user.update()
				db.session.commit()

				if worker.is_authenticated:
					return redirect(url_for('index.index'))
				if request.device.credential:
					return redirect(url_for('auth.passkey'))
				return redirect(url_for('auth.password'))
	return redirect(url_for('auth.phishing'))

@auth.route("/verify", methods=['GET', 'POST'])
def verify(user=None, email=None, error=list()):
	error.clear();
	if 'identity' in session:
		if user := User.query.filter_by(id=session.get('identity')).first():
			session['email'] = email = user.email
			session['identity'] = user.get_id()
		else:
			error.clear(); error.append('user')
		if not error and user:
			url = url_for('confirm', token=request.device.token())
			url = app.config.get('SERVER_HSTS') + '://' \
				  + app.config.get('SERVER_HOST') + url
			print(url)
			request.device.mail(to=[user.email],
								cc=[],
								bcc=[],
								subject="Email confirmation needed",
								title=dict(title='Email confirmation needed',
										   text=['We have received a request to authorize this email address for use with relock Inc. demo service.'],
										   separators=['', '']),
								button=dict(title='Accept and verify your email',
									  		text=['{{ link }}'],
									  		separators=['', '']),
								intro=dict(title='Dear, {{ user }}!',
									  	   text=['You requested a new email address connected with your account.',
									  		 	 'If you wish to accept the new email address, copy the link below and paste it into your active sign-in tab or click the button in this message.',
									  		 	 'Please take extra care to ensure that the link points to a legitimate domain {{ host }}']),
								recomended=dict(title='How to confirm and verify the email?',
									  			text=['Click on the button in this e-mail message or copy the link below into browser and then follow the instructions that will appear in your screen.',
									  				  '{{ link }}',
									  				  'Keep in mind that the email address verification process only takes place once, so if you are using the browser and email address that has already been verified, you may have been the victim of a phishing attack.']),
								explanation=dict(title='What if I\'m not signing on at this moment to service?',
									  			 text=['If you didn\'t request this message and are not currently trying to sign on into the service, you are most likely the victim of a cyber attack. Your login and password have been compromised and a malicious attacker is trying to gain access to your account.',
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
	return render_template('verify.html', error=error)
