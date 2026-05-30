"""Development settings."""
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['*']

# More verbose logging in dev
LOGGING['root']['level'] = 'DEBUG'  # noqa: F405

# Console email backend for local development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Allow all CORS origins in development for simpler testing
CORS_ALLOW_ALL_ORIGINS = True
