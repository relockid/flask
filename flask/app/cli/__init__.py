import click
import os

@click.group()
def cli():
	""" re:lock managment tools. """
	pass
	
from .demo import *