import re
import smtplib
import ssl

from os import environ as env
from flask import current_app as app
from flask import render_template
from threading import Thread

import logging, warnings, os, sys

try: 
	from flask_mail import Mail as Mailer, Message
except ImportError:
	Mailer = None
	Message = object
	logging.debug('Postfix is not available, ')

class Mail(Message):

	__slots__ = ['recipients', '_cc', '_subject', '_text', '_html', '__template']

	def __init__(self, template=None, *args, **kwargs):
		self.recipients = []
		self._cc = []
		if template:
			self.__template = template

	def to(self, *args):
		for addr in args:
			if not isinstance(addr, str):
				warnings.warn(f'Bad email address: {addr}')
			self.recipients.append(addr)
		return self

	def cc(self, *args):
		for addr in args:
			if not isinstance(addr, str):
				warnings.warn(f'Bad email address: {addr}')
			self._cc.append(addr)
		return self

	def text(self, *args, **kwargs):
		self._text = render_template('emails/%s/%s.txt' % (self.__template, self.__template), *args, **kwargs)
		self._text = re.sub(r'\n', '\r\n', self._text)
		return self

	def html(self, *args, **kwargs):
		self._html = render_template('emails/%s/%s.html' % (self.__template, self.__template), *args, **kwargs)
		self._text = re.sub(r'\n', '\r\n', self._text)
		return self

	def subject(self, subject):
		self._subject = subject
		return self

	def get(self, *args):
		self.to(*args)
		self.cc()
		msg = Message(self._subject, 
					  sender=app.postfix.sender,
					  recipients=list(self.recipients), 
					  cc=self._cc)
		if hasattr(self, '_text'):
			msg.body = self._text
		if hasattr(self, '_html'):
			msg.html = self._html

		return msg

	def send(self, *args, threading=False):
		self.to(*args)
		self.cc()
		msg = Message(self._subject, 
					  sender=app.postfix.sender, 
					  recipients=self.recipients, 
					  cc=self._cc)
		if hasattr(self, '_text'):
			msg.body = self._text
		if hasattr(self, '_html'):
			msg.html = self._html

		if threading:
			Thread(target=app.postfix.send,
				   args=(app._get_current_object(), 
						 list(self.recipients), 
						 list(self._cc), 
						 str(msg))).start()
		else:
			app.postfix.postfix.send(app._get_current_object(), 
									 list(self.recipients), 
									 list(self._cc), 
									 str(msg))

class Postfix(object):

	__slots__ = ['postfix', 'sender', 'server']

	def __init__(self, *args, **kwargs):
		if Mailer is not None:
			self.postfix = Mailer()

	def init_app(self, app):
		if Mailer is not None:
			app.config.setdefault('MAIL_SERVER', env.get('MAIL_SERVER', None))
			app.config.setdefault('MAIL_PORT', env.get('MAIL_PORT', 587))
			app.config.setdefault('MAIL_USE_SSL', env.get('MAIL_USE_SSL', False))
			app.config.setdefault('MAIL_USE_TLS', env.get('MAIL_USE_TLS', True))
			app.config.setdefault('MAIL_DEBUG', env.get('MAIL_DEBUG', 1))
			app.config.setdefault('MAIL_USERNAME', env.get('MAIL_USERNAME', None))
			app.config.setdefault('MAIL_PASSWORD', env.get('MAIL_PASSWORD', None))
			app.config.setdefault('MAIL_REPORT', env.get('MAIL_REPORT', False))
			app.config.setdefault('MAIL_ERRORS', env.get('MAIL_ERRORS', None))
			app.config.setdefault('MAIL_DEFAULT_SENDER', env.get('MAIL_DEFAULT_SENDER', None))

			self.postfix.init_app(app)
			try:
				self.server  = smtplib.SMTP(app.config.get('MAIL_SERVER'), 
											app.config.get('MAIL_PORT'))
			except Exception:
				self.server = None
				self.sender = None
			else:
				self.sender = app.config.get('MAIL_DEFAULT_SENDER')
			setattr(app, 'postfix', self)
		else:
			logging.error('Mail function not available, there is no Flask-Mail.')

	@staticmethod
	def send(app, to, cc, msg):
		with app.app_context():
			context = ssl.create_default_context()
			with smtplib.SMTP(app.config.get('MAIL_SERVER'), 
							  app.config.get('MAIL_PORT')) as server:
				server.ehlo()
				server.starttls(context=ssl.create_default_context()) # Secure the connection
				server.ehlo() # Can be omitted
				server.login(app.config.get('MAIL_USERNAME'), 
							 app.config.get('MAIL_PASSWORD'))
				for email in to:
					server.sendmail(app.postfix.sender, email, msg)
				for email in cc:
					server.sendmail(app.postfix.sender, email, msg)
				server.quit()

	@classmethod
	def __new__(cls, *args, **kwargs): # __new__ always a classmethod
		if not hasattr(cls, 'instance'):
			cls.instance = super(Postfix, cls).__new__(cls)
		return cls.instance
