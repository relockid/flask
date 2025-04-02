from gevent import monkey

monkey.patch_all()

import logging
import os
import base64
import redis as redis

from flask import Flask, url_for
from flask_session import Session
from flask_login import LoginManager as Login
from flask_bootstrap import Bootstrap5 as Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_compress import Compress

from datetime import timedelta

from .models import Base
from .plugins.mail import Postfix as Mail

try:
	from relock import (Flask as Relock,
						Cloud,
						Nobody)
except Exception:
	try:
		from sdk.src.relock import (Flask as Relock,
									Cloud,
									Nobody)
	except Exception:
		logging.error('Session sentinel is not available.')

db = SQLAlchemy(model_class=Base)
bootstrap = Bootstrap()
session = Session()
login = Login()
nobody = Nobody()
compress = Compress()
mail = Mail()
relock = Relock()
cloud = Cloud()

def init_app(*args, **kwargs):


	""" Initialize the core application. """
	app = Flask(__name__, instance_relative_config=False)

	app.config['SERVER_HSTS'] = 'https' if int(kwargs.get('port', 443)) else 'http'
	app.config['SERVER_HOST'] = str(kwargs.get('host'))
	app.config['SERVER_BIND'] = str(kwargs.get('ip'))
	app.config['SERVER_PORT'] = int(kwargs.get('port', 443))
	app.config['APP_DEBUG'] = bool(kwargs.get('debug', False))

	""" Flask_Session configuration """
	app.config['REDIS_HOST'] = os.environ.get('REDIS_HOST', '127.0.0.1')
	app.config['REDIS_PORT'] = os.environ.get('REDIS_PORT', 6379)
	app.config['REDIS_DB'] = os.environ.get('REDIS_DB', 0)

	app.config['SESSION_COOKIE_DOMAIN'] = None
	app.config['SESSION_COOKIE_PATH'] = '/'
	app.config['SESSION_COOKIE_NAME'] = 'session'
	app.config['SESSION_COOKIE_HTTPONLY'] = True
	app.config['SESSION_COOKIE_SECURE'] = True
	app.config['SESSION_COOKIE_SAMESITE'] = 'lax'
	app.config['SESSION_USE_SIGNER'] = True
	app.config['SESSION_PROTECTION'] = 'strong'
	app.config['SESSION_PERMANENT'] = False
	app.config['SESSION_REFRESH_EACH_REQUEST'] = True
	# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)
	app.config['REMEMBER_ME'] = False
	# app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
	app.config['REMEMBER_COOKIE_SECURE'] = True

	app.config['SESSION_TYPE'] = 'redis'
	app.config['SESSION_REDIS'] = redis.Redis(host=app.config.get('REDIS_HOST'), 
										   	  port=app.config.get('REDIS_PORT'), 
										      db=app.config.get('REDIS_DB'), 
										      decode_responses=False)

	""" app SECRET_KEY stored in redis """
	if _ := app.config.get('SESSION_REDIS'):
		if not _.get('SECRET_KEY'):
			_.set('SECRET_KEY', os.urandom(32))
		app.config['SECRET_KEY'] = _.get('SECRET_KEY')

	""" MySQL configuration """
	app.config['DB_USER'] = os.environ.get('DB_USER', 'admin')
	app.config['DB_NAME'] = os.environ.get('DB_NAME', 'demo')
	app.config['DB_HOST'] = os.environ.get('DB_HOST', '127.0.0.1')
	app.config['DB_PORT'] = os.environ.get('DB_PORT', 3306)
	app.config['DB_PASS'] = os.environ.get('DB_PASS', '')
	app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'\
											+ app.config.get('DB_USER')\
											+ ':' + app.config.get('DB_PASS')\
											+ '@' + app.config.get('DB_HOST')\
											+ ':' + str(app.config.get('DB_PORT'))\
											+ '/' + app.config.get('DB_NAME')
	app.config['CAEP_ENABLED'] = os.environ.get('CAEP_ENABLED', False)
	app.config['OTEL_ENABLED'] = os.environ.get('OTEL_ENABLED', False)

	with app.app_context() as context:

		""" Initialize extensions """
		db.init_app(app)
		session.init_app(app)
		login.init_app(app)
		bootstrap.init_app(app)
		nobody.init_app(app)
		mail.init_app(app)
		compress.init_app(app)
		relock.init_app(app)
		cloud.init_app(app)
		
		""" Load endpoints """
		from .routes.auth import _; app.register_blueprint(_)
		from .routes.index import _; app.register_blueprint(_)
		from .routes.simulator import _; app.register_blueprint(_)
		from .routes.errors import _; app.register_blueprint(_)

		db.create_all(); setattr(app , 'db', db)

		""" Expose unprotected routes

			These routes will be publicly available even if the user is not 
			authenticated and the device is not authorised to receive 
			responses. Authentication and device authorisation are required 
			for private routes (all not listed here).
		"""
		app.expose.append('/auth/device')
		app.expose.append('/auth/clear')
		app.expose.append('/auth/identity')
		app.expose.append('/auth/signon')
		app.expose.append('/auth/approve')
		app.expose.append('/auth/ticket')
		app.expose.append('/favicon.ico')

		""" Load App contexts """
		from .contexts import (request_nonce_processor,
							   after_request,
							   preflight,
							   ico)
	return app
