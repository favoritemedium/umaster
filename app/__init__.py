from flask import Flask
from flask.ext.session import Session
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config.from_object('config')
Session(app)

from app import views
