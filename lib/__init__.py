from flask import Flask
from flask_bootstrap import Bootstrap
import json

app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'b\';\x03\x95c{\xe2E\xef\xe6tB\t\x94J\x94\xed<\xf0\x7f\xcb\xbeD\x97l\''

app.config.from_file('config.json', load=json.load)

from lib import views