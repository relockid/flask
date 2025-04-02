import sys
import time
import requests
import logging
import click
import os
import binascii
import base64
import signal
import dotenv
import ssl

try:
	import werkzeug
except:
	pass

from . import cli

from typing import Any
from gevent import sleep

from multiprocessing import Process, current_process, cpu_count

from gevent import get_hub
from gevent.pywsgi import WSGIServer 
from gevent.server import _tcp_listener

logging.basicConfig(level=0)
logging.getLogger('cli.client')

class devnull:
	write = lambda _: None
	
from datetime import timedelta

@click.option('--host', is_flag=False, default='0.0.0.0', help=('Host or IP, host:port API.'))
@click.option('--port', is_flag=False, default=443, help=('API port number. Default :80'))
@click.option('--ip', is_flag=False, default='0.0.0.0', help=('IP to assign'))
@click.option('--key', is_flag=False, default='key.pem', help=('Key certyficate'))
@click.option('--crt', is_flag=False, default='cert.pem', help=('Crt file'))
@click.option('--db_host', is_flag=False, default=str(), help=('Database host'))
@click.option('--cache_host', is_flag=False, default=str(), help=('Cache host'))
@click.option('--sentinel_host', is_flag=False, default=str(), help=('Sentinel host'))
@click.option('--debug', is_flag=True, default=True, help=('Debug mode. Default: True'))
@cli.command()
def demo(host, 
		 port,
		 ip,
		 key,
		 crt,
		 db_host,
		 cache_host,
		 sentinel_host,
		 debug):
	dotenv.load_dotenv()

	if db_host:
		os.environ['DB_HOST'] = db_host
	if cache_host:
		os.environ['REDIS_HOST'] = cache_host
	if sentinel_host:
		os.environ['SESSION_SENTINEL_HOST'] = sentinel_host

	from .. import init_app

	if port == 443:
		context = (crt, key)
	else:
		context = None
	
	app = init_app(host=host, 
				   ip=ip, 
				   port=port,
				   debug=debug)
	app.run(debug=debug,
			host=ip or host,
			port=port,
			ssl_context=context)

@click.option('--host', is_flag=False, default='127.0.0.1', help=('Host or IP, host:port API.'))
@click.option('--port', is_flag=False, default=443, help=('API port number. Default :80'))
@click.option('--ip', is_flag=False, default='0.0.0.0', help=('IP to assign'))
@click.option('--cpus', is_flag=False, default=0, help=('Number of cpus to use'))
@click.option('--key', is_flag=False, default='key.pem', help=('Key certyficate'))
@click.option('--crt', is_flag=False, default='cert.pem', help=('Crt file'))
@click.option('--debug', is_flag=True, default=None, help=('Debug mode. Default: True'))
@click.option('--db_host', is_flag=False, default=str(), help=('Database host'))
@click.option('--cache_host', is_flag=False, default=str(), help=('Cache host'))
@click.option('--sentinel_host', is_flag=False, default=str(), help=('Sentinel host'))
@click.option('--multiprocessing', is_flag=True, default=False, help=('Start multiprocessing mode.'))
@cli.command()
def run(host, 
		port,
		ip,
		cpus,
		key,
		crt,
		debug,
		db_host,
		cache_host,
		sentinel_host,
		multiprocessing):
	dotenv.load_dotenv()

	if db_host:
		os.environ['DB_HOST'] = db_host
	if cache_host:
		os.environ['REDIS_HOST'] = cache_host
	if sentinel_host:
		os.environ['SESSION_SENTINEL_HOST'] = sentinel_host

	from .. import init_app

	logging.info('Starting WSGIServer...')

	def process(listener, x, context):
		app = init_app(host=host,
					   ip=ip,
					   port=port,
					   debug=debug)

		if context:
			server = WSGIServer(listener, 
								app,
								ssl_context=context,
								log=devnull)
		else:
			server = WSGIServer(listener, 
								app,
								log=devnull)

		logging.info('Serving worker process app[%s]/pid[%s]', x, os.getpid())

		def stop(*args, **kwargs):
			server.stop()
			server.close()
			
		for sig in (
			signal.SIGHUP,
			signal.SIGINT,
			signal.SIGTERM,
			signal.SIGQUIT,
		):
			signal.signal(sig, stop)
		server.serve_forever()

	if listener := _tcp_listener((ip or host,
							  	  port), reuse_addr=True):
		if os.path.isfile(crt) and os.path.isfile(key):
			context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
			context.minimum_version = ssl.TLSVersion.TLSv1_2
			context.options |= ssl.OP_NO_TLSv1
			context.options |= ssl.OP_NO_TLSv1_1
			context.options |= ssl.OP_NO_SSLv2
			context.options |= ssl.OP_NO_SSLv3
			context.load_cert_chain(crt, keyfile=key)
		else:
			context = None

		if multiprocessing:
			for x in range(int(cpus) or cpu_count()):
				Process(target=process, args=(listener, x, context), name=f'HTTP {x}').start()
		process(listener, os.getpid(), context)
