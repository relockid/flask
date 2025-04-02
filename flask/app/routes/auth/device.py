from . import _ as auth, logging

from flask import (current_app as app,
				   render_template,
				   session,
				   request,
				   redirect,
				   url_for,
				   flash,
				   abort)

from ...models.user import User

@auth.route('/forbidden', methods=['GET'])
def forbidden(error=list()):
	return render_template('forbidden.html', error=error)

@auth.route('/device', methods=['GET'])
def device(error=list()):
	return render_template('device.html', error=error)

@auth.route('/clear', methods=['GET'])
def clear(token=None, error=list()):
	if request.device.clear():
		return render_template('clear.html', url=url_for('index.index'))
	return redirect(url_for('index.index'))
