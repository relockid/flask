import json 

from . import _ as auth, logging

from flask import (current_app as app,
				   render_template,
				   session,
				   request,
				   redirect,
				   Response,
				   url_for,
				   flash,
				   abort)

from ...models.user import User

@auth.route('/resiliency', methods=['GET'])
def resiliency(error=list()):
	return render_template('resiliency.html')

@auth.route('/forbidden', methods=['GET'])
def forbidden(error=list()):
	if devices := request.device.devices(session.get('identity')):
		return render_template('forbidden.html', devices=devices)
	return render_template('forbidden.html')

@auth.route('/device', methods=['GET'])
def device(error=list()):
	return render_template('device.html', error=error)

@auth.route('/clear', methods=['GET'])
def clear(token=None, error=list()):
	return redirect(url_for('relock.clean'))
