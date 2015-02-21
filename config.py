import os

CSRF_ENABLED = True
SECRET_KEY = os.environ.get('SECRET_KEY', "not-so-secret-key")
DEBUG = os.environ.get('DEBUG') == "True"

# the session store needs to be large enough to store all the tickets
SESSION_TYPE = "filesystem"
