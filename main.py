import logging
from gevent import monkey

monkey.patch_all()

from app import init_app
from app.cli import *

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
	cli()