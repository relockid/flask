from flask import Blueprint
import os, logging

logging = logging.getLogger(__name__)

_ = os.path.basename(os.path.dirname(__file__))
_ = Blueprint(_, __name__, url_prefix='/%s' % _,
						   template_folder='templates',
						   static_folder='static',
						   static_url_path='/static/%s' % _)
from .routes import *
from .signin import *
from .signon import *
from .forgot import *
from .identity import *
from .password import *
from .passkey import *
from .passkey_remove import *
from .device import *
from .unrecognised import *
from .phishing import *
from .approve import *
from .unlink import *
from .delete import *
from .verify import *