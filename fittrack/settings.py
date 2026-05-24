"""
Django settings for FitTrack.

Reads sensitive values from environment variables so nothing secret
is ever committed to version control (rubric 5.2 / 5.3).

Works for both:
  - Local development (VS Code + .env file)
  - Heroku production (env vars set via heroku config:set)
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# Load .env file when running locally — no-op on Heroku (vars already in env)
load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ───────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'changeme-only-for-local-dev')

# Set DEBUG=True in your .env for local development.
# On Heroku: heroku config:set DEBUG=False
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Disable template context copying for Python 3.14 compatibility
TEST_DISABLE_TEMPLATE_CONTEXT_COPY = True

# Accepts a space-separated list, e.g. "localhost 127.0.0.1 myapp.herokuapp.com"
_allowed = os.environ.get('ALLOWED_HOSTS', 'localhost 127.0.0.1')
ALLOWED_HOSTS = _allowed.split()

# Required in Django 4.x for CSRF to work on HTTPS hosts (e.g. Heroku)
_csrf_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [o for o in _csrf_origins.split() if o]

# ── Application definition ─────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tracker',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fittrack.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Look in the top-level templates/ folder as well as each app
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fittrack.wsgi.application'

# ── Database ───────────────────────────────────────────────────────────────
# dj-database-url parses DATABASE_URL automatically.
# Heroku sets DATABASE_URL for you. Locally it comes from .env.
# ssl_require=True is needed on Heroku; False locally (no SSL on localhost).
_db_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/fittrack')
DATABASES = {
    'default': dj_database_url.config(
        default=_db_url,
        conn_max_age=600,
        ssl_require='localhost' not in _db_url and '127.0.0.1' not in _db_url,
    )
}

# ── Password validation ────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Auth redirects ─────────────────────────────────────────────────────────
LOGIN_URL           = '/login/'
LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# ── Internationalisation ───────────────────────────────────────────────────
LANGUAGE_CODE = 'en-gb'
TIME_ZONE     = 'Europe/London'
USE_I18N      = True
USE_TZ        = True

# ── Static files ───────────────────────────────────────────────────────────
STATIC_URL       = '/static/'
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

_static_backend = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
    if os.environ.get('USE_MANIFEST_STORAGE') == '1'
    else 'django.contrib.staticfiles.storage.StaticFilesStorage'
)
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': _static_backend},
}

# ── Email ──────────────────────────────────────────────────────────────────
# Locally falls back to console (prints to terminal). On Heroku set:
#   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
#   EMAIL_HOST / EMAIL_PORT / EMAIL_HOST_USER / EMAIL_HOST_PASSWORD
EMAIL_BACKEND       = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.sendgrid.net')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@fittrack.app')

# ── Misc ───────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django messages use 'error' tag but Bootstrap/our CSS uses 'danger'
from django.contrib.messages import constants as message_constants  # noqa: E402
MESSAGE_TAGS = {message_constants.ERROR: 'error'}
