from flask import Flask
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from flask_hashing import Hashing
from flask_login import LoginManager
import json

# Create a WSGI Application
app = Flask(__name__)

# Do some configuration
app.secret_key = 'b\';\x03\x95c{\xe2E\xef\xe6tB\t\x94J\x94\xed<\xf0\x7f\xcb\xbeD\x97l\''
app.config.from_file('config.json', load=json.load)

# Initialize extensions
Bootstrap(app)
mongo = PyMongo(app)
hasher = Hashing(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'Please login to access this page'

from lib import views