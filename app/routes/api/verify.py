import bleach
import hashlib

from datetime import datetime

from . import _ as bp, logging
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

conf = dict(NAME='Relock-Server',
			VERSION='0.6.2',
			HOST='relock.demo',
			PROTOCOL='https',
			BLUEPRINT='relock',
			MAIN='main',
			IP='0.0.0.0',
			SESSION_TTL=60,
			SESSION_INTERIM_TTL=3600,
			REQUEST_TTL=10,
			USER_TTL=60,
			USER_PERSIST_TTL=2592000,
			DEVICE_TTL=30,
			DEVICE_INTERIM_TTL=600,
			DEVICE_PERSIST_TTL=2592000,
			REKEYING_NONCE_TTL=1,
			RELOCK_SERVICE_TIMEOUT=30,
			RELOCK_SERVICE_TAB_LOGOUT=True,
			RELOCK_SERVICE_MULTITABS=True,
			RELOCK_SERVICE_PROTECTED=True,
			RELOCK_SERVICE_REPROCEST=True,
			RELOCK_SERVICE_LOGOUT=True,
			RELOCK_SERVICE_REPROCESS=True,
			RELOCK_JS_MAX_AGE=0,
			RELOCK_ABORT_WHEN_NETWORK_CHANGE=True,
			RELOCK_ABORT_ON_BAD_REQUEST=True,
			RELOCK_ABORT_ON_CONFLICT=True,
			RELOCK_ABORT_WHEN_GONE=True,
			COOKIE_DOMAIN=str(),
			COOKIE_PATH='/',
			LOGIN_COOKIE_NAME='X-Key-Data',
			LOGIN_COOKIE_SAMESITE='lax',
			STAMP_COOKIE_NAME='X-Key-Stamp',
			STAMP_COOKIE_SAMESITE='lax',
			XSESS_COOKIE_NAME='X-Key-Session',
			XSESS_COOKIE_SAMESITE='lax',
			XSESS_COOKIE_TIME=3600,
			SESSION_CACHE='relock_cache',
			SESSION_MAX_TIME=3600,
			CAEP_ENABLED=False,
			OTEL_ENABLED=False,
			MAIL_SERVER='email-smtp.eu-central-1.amazonaws.com',
			MAIL_PORT=587,
			MAIL_USE_SSL=False,
			MAIL_USE_TLS=True,
			MAIL_DEBUG=1,
			MAIL_USERNAME='',
			MAIL_PASSWORD='',
			MAIL_REPORT=False,
			MAIL_ERRORS=None,
			MAIL_DEFAULT_SENDER='relock security <no-reply@relock.security>')

@bp.route('/remote', methods=['GET', 'POST'])
@bp.route('/remote/<string:key>', defaults={'key': str()}, methods=['GET', 'POST'])
def remote(key=str()):
	if key := bleach.clean(request.headers.get('Member-ID', key)):
		if user := User.query.filter_by(key=key).first():
			return conf
	return dict()