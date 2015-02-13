from flask import Flask
from flask.ext.session import Session

app = Flask(__name__)
app.config.from_object('config')
Session(app)
from app import views
