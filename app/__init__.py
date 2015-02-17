from flask import Flask
from flask_sslify import SSLify
from flask.ext.session import Session
import os

app = Flask(__name__)
if 'DYNO' in os.environ:
    sslify = SSLify(app)  # force ssl on heroku

app.config.from_object('config')
Session(app)
from app import views
