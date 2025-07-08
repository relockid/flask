from flask import render_template
from . import _ as bp, logging


@bp.app_errorhandler(401)
def not_found_error(error):
    return render_template('401.html', code=error.code,
                                       description=error.description), 401

@bp.app_errorhandler(403)
def not_found_error(error):
    return render_template('403.html', code=error.code,
                                       description=error.description), 403

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html', code=error.code,
                                       description=error.description), 404

@bp.app_errorhandler(400)
def not_found_error(error):
    return render_template('400.html', code=error.code,
                                       description=error.description), 400
@bp.app_errorhandler(500)
def internal_error(error):
    return render_template('500.html', code=error.code,
                                       description=error.description), 500
