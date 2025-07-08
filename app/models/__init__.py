from flask import current_app as app
from datetime import datetime

# from .. import db
from sqlalchemy import Integer, String, DateTime, Column
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):

	cache_ok = True

	def __init__(self, commit=False, *args, **kwargs):
		if commit is True:
			for key in self:
				if kwargs.get(key):
					setattr(self, key, kwargs.get(key, None))
			self.save()

	def save(self, **kwargs):
		if not self.id:
			self.__save__ = True
			app.db.session.add(self)
			app.db.session.commit()
		return self

	def update(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)
		app.db.session.merge(self)
		app.db.session.commit()
		return self


	id = Column(Integer, index=True, 
						 primary_key=True, 
						 autoincrement=True, 
						 nullable=False, 
						 unique=True)
	created = Column(DateTime, index=True, 
							   server_default=func.now(), 
						  	   default=func.now(), 
							   nullable=True)