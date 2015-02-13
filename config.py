import os

CSRF_ENABLED = True
SECRET_KEY = os.urandom(24)

SESSION_TYPE = "filesystem"
