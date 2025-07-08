from uuid import uuid4
from .. import db
from typing import Any

import logging, re

from . import Base

class Company(Base):

	# __table__ = 'company'
	__tablename__ = 'company'

	name = db.Column(db.String(128), index=True, nullable=False, unique=True)
	address = db.Column(db.String(255), index=False, nullable=True)
