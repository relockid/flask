from __future__ import annotations

import logging, re

from datetime import datetime
from flask import current_app as app, session
from flask_login import UserMixin, login_user, logout_user, current_user as worker
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login, db

from . import Base
from .company import Company

class Logic(object):

	def __init__(self, commit=True, *args, **kwargs):
		if commit is True:
			if kwargs.get('email') and not self.email:
				self.email = kwargs.get('email')
			if kwargs.get('password') and not self.password:
				self.password = generate_password_hash(kwargs.get('password'))
			self.save() if not self.id else self.update()

	def change_password(self, password:str) -> User:
		return self.update(password=generate_password_hash(password))

	def check_password(self, password:str) -> bool:
		if self.password:
			return check_password_hash(self.password, password)
		return False

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	@property
	def is_strict(self):
		return False

	def get_id(self):
		return int(self)

	def get_email(self):
		return str(self.email)

	@staticmethod
	@login.user_loader
	def load(id:int) -> User:
		return User.query.get(int(id))

	def login(self, remember:bool=False) -> bool:
		if login_user(self, remember=app.config.get('REMEMBER_ME', remember)):
			return True
		return False

	def logout(self) -> bool:
		if self.is_authenticated and logout_user():
			return True
		return False

	def __int__(self):
		return int(self.id or 0)

	def __str__(self):
		return str(self.email)


class User(Logic, Base, UserMixin, db.Model):

	__tablename__ = 'user'

	email = db.Column(db.String(128), index=True, unique=True, nullable=False)
	password = db.Column(db.String(256), nullable=False)
	seen = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=True)
	protected = db.Column(db.Boolean(), nullable=True, default=0)
	veryficated = db.Column(db.Boolean(), nullable=True, default=0)
	key = db.Column(db.String(255), nullable=True, default=0)
