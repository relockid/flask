from flask import (current_app as app, 
				   request,
				   session,
				   redirect,
				   url_for)
from flask_login import current_user as worker

from pwd import getpwnam
from grp import getgrnam

import base64
import logging
import os

@app.login_manager.unauthorized_handler
def unauthorized_callback():
	return redirect(url_for('auth.device'))

@app.login_manager.needs_refresh_handler
def refresh():
	logging.error('refresh logout')
	return redirect(url_for('auth.logout'))

@app.context_processor
def request_nonce_processor():
	def request_nonce():
		return getattr(app, '__nonce')
	return dict(request_nonce=request_nonce)

@app.context_processor
def request_counter_processor():
	def request_counter():
		if not session.get('request_counter'):
			session['request_counter'] = 0
		session['request_counter'] = session.get('request_counter') + 1
		return session.get('request_counter')
	return dict(request_counter=request_counter)

@app.after_request
def after_request(response):
	if request.url == '/favicon.ico':
		return response

	response.headers.add("Access-Control-Allow-Origin", app.config.get('SERVER_HOST'))
	response.headers.add("Access-Control-Allow-Headers", "Origin, Accept, X-Requested-With, Accept-Language, Credentials, Content-Type, Accept-Encoding, Upgrade-Insecure-Requests");
	response.headers.add('Access-Control-Allow-Methods', "GET, POST, OPTIONS")
	response.headers.add('Access-Control-Allow-Credentials',  'true')
	response.headers.add('Access-Control-Allow-Local-Network','false')
	response.headers.add('Access-Control-Allow-Private-Network', 'true')
	response.headers.add('Access-Control-Expose-Headers', '*, Authorization, Content-Type')
	response.headers.add('Access-Control-Max-Age', 600)
	response.headers.add('Vary', 'Access-Control-Request-Headers, Access-Control-Request-Method')
	response.headers.add('Server', 're:lock')
	response.headers.add('X-Frame-Options', 'DENY')
	response.headers.add('X-Powered-By', 're:lock')
	response.headers.add('X-Content-Type-Options', 'nosniff')
	response.headers.add('Referrer-Policy', 'no-referrer, strict-origin-when-cross-origin')
	response.headers.add('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload')
	response.headers.add('X-Permitted-Cross-Domain-Policies', 'none')
	response.headers.add('Content-Security-Policy', 
						 'default-src \'self\' \'unsafe-eval\'; \
						  connect-src \'self\' fonts.gstatic.com fonts.googleapis.com cdnjs.cloudflare.com; \
						  style-src \'self\' cdn.jsdelivr.net fonts.gstatic.com fonts.googleapis.com; \
						  font-src \'self\' fonts.gstatic.com fonts.googleapis.com  https:; \
						  script-src \'strict-dynamic\' cdn.jsdelivr.net \'nonce-' + getattr(app, '__nonce') + '\' \'unsafe-inline\'; \
						  object-src \'none\'; \
						  base-uri \'none\'; \
						  img-src \'self\' data: content:; \
						  frame-ancestors \'self\'; \
						  media-src   *;')

	if app.config.get('APP_DEBUG'):
		_ = (500, 400, 401, 403, 404)
		if response.status_code in _:
			logging.debug("[{w}%s/{z}{red}%s{z}{gray}]{z} {red}%s{z} {gray}%s{x}", request.method, response.status_code, request.remote_addr, request.path)
		else:
			logging.debug("[{w}%s/{z}{green}%s{z}{gray}]{z} %s {gray}%s{x}", request.method, response.status_code, request.remote_addr, request.path)
	return response

@app.before_request
def preflight():
	setattr(app, '__nonce', base64.urlsafe_b64encode(os.urandom(8)).decode())
	if request.method.lower() == 'options':
		if response := Response(None, 204):
			response.headers.add('Access-Control-Max-Age', 600)
			return response

@app.route('/favicon.ico')
def ico():
	return '<?xml version="1.0" encoding="UTF-8"?> \
			<svg viewBox="0 0 767.99 626.68" xmlns="http://www.w3.org/2000/svg"> \
			<defs> \
			<style>.cls-1 { \
			        fill: #c0ff00; \
			      } \
			      .cls-2 { \
			        fill: #211f54; \
			      }</style> \
			</defs> \
			<path class="cls-2" d="M295.88,265.34v40.52h-22.82c-8.63,0-16.06,1.82-22.3,5.45-6.25,3.63-11.07,8.91-14.47,15.83-3.41,6.93-5.11,15.15-5.11,24.69l-.55,89.36h-45l-.42-175.85h42.57v24.2c3.92-4.84,8.47-9.05,13.62-12.62,11.12-7.72,23.94-11.58,38.47-11.58h16.01Z"/> \
			<path class="cls-2" d="m468.3 307.51c-7.28-14.31-17.38-25.44-30.33-33.39-12.95-7.96-28.17-11.93-45.65-11.93s-33.28 3.86-46.68 11.59c-13.41 7.73-23.92 18.51-31.52 32.37-7.62 13.85-11.42 29.87-11.42 48.04s3.86 34.18 11.59 48.04c7.72 13.86 18.45 24.65 32.2 32.37 13.74 7.72 29.69 11.58 47.87 11.58s33.67-4.08 47.19-12.26c13.51-8.19 23.8-19.99 30.83-35.44l-36.8-15.33h-4.09c-3.86 7.28-9.2 13.07-16.01 17.38s-13.86 6.47-21.12 6.47c-8.18 0-15.73-2.05-22.67-6.13-6.92-4.09-12.49-9.49-16.69-16.19-2.72-4.33-4.56-8.94-5.51-13.8h124.61l5.11-5.11v-8.18c0-19.08-3.64-35.78-10.91-50.09zm-118.59 26.92c0.92-4.35 2.45-8.39 4.6-12.1 3.74-6.47 9.03-11.59 15.84-15.33 6.81-3.75 14.54-5.62 23.18-5.62 7.72 0 14.7 1.76 20.95 5.28 6.24 3.52 11.25 8.47 14.99 14.82 2.32 3.93 3.91 8.25 4.8 12.95h-84.37z"/> \
			<polygon class="cls-1" points="465.14 182.57 539.91 447.12 587.17 447.12 512.41 182.57"/> \
			</svg> \
			'