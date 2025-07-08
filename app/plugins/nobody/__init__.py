from flask import current_app as app

from pwd import getpwnam
from grp import getgrnam

import os
import pwd
import grp
import logging

class Nobody(object):

	def __init__(self, app=None, uid_name=None, gid_name=None):
		self.uid_name = os.environ.get('APP_UID', uid_name)
		self.gid_name = os.environ.get('APP_GID', gid_name)

		if app is not None:
			self.init_app(app)

	def init_app(self, app, add_context_processor=True):
		"""
		Configures an application. This registers an `before_request` call, and
		attaches this `NobodyManager` to it as `app.worker_manager`.

		:param app: The :class:`flask.Flask` object to configure.
		:type app: :class:`flask.Flask`
		:param add_context_processor: Whether to add a context processor to
			the app that adds a `current_user` variable to the template.
			Defaults to ``True``.
		:type add_context_processor: bool
		"""
		app.worker_manager = self
		
		app.config.setdefault('APP_UID', self.uid_name or 'nobody')
		app.config.setdefault('APP_GID', self.gid_name or 'nogroup')

		with app.app_context():
			app.before_request(self.ensure_user)

	def ensure_user(self):
		self._uid = os.getuid()
		self._gid = os.getgid()

		if self._uid == 0:
			# If we started as root, drop privs and become the specified user/group
			logging.info('drop_privileges: running as %s' % pwd.getpwuid(self._uid)[0])
			logging.info('drop_privileges: started as %s/%s' % \
								 (pwd.getpwuid(self._uid)[0],
								  grp.getgrgid(self._gid)[0]))
			self.change_user_group()
		# We're not root so, like, whatever dude

	def change_user_group(self):

		# Get the uid/gid from the name
		running_uid = pwd.getpwnam(app.config.get('APP_UID'))[2]
		running_gid = grp.getgrnam(app.config.get('APP_GID'))[2]

		# Try setting the new uid/gid
		try:
			os.setgid(running_gid)
		except OSError as e:
			logging.warning('Could not set effective group id: %s' % e)

		try:
			os.setuid(running_uid)
		except OSError as e:
			logging.warning('Could not set effective user id: %s' % e)

		# Ensure a very convervative umask
		new_umask = 0o777
		old_umask = os.umask(new_umask)
		logging.info('drop_privileges: Old umask: %s, new umask: %s' % \
				 (oct(old_umask), oct(new_umask)))

		final_uid = os.getuid()
		final_gid = os.getgid()
		logging.info('drop_privileges: running as %s/%s' % \
				 (pwd.getpwuid(final_uid)[0],
				  grp.getgrgid(final_gid)[0]))