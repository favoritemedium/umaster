import os

CSRF_ENABLED = True
SECRET_KEY = os.environ['SECRET_KEY'] or "not-so-secret-key"

SESSION_TYPE = "filesystem"

DEBUG=True
