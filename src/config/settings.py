# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

"""Django settings."""

from pathlib import Path

import environ  # type: ignore [import-untyped]
import sentry_sdk
from django.core.exceptions import DisallowedHost

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR.parent / '.env')

DEBUG = env('DEBUG')

SECRET_KEY = env('SECRET_KEY', default='S3cRet')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',

    'main',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': env.db(),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'static'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = ['https://revive-code-bot.ilaletdinov.ru']

BASIC_AUTH_TOKEN = env('BASIC_AUTH_TOKEN')

GH_APP_KEY = (BASE_DIR / 'revive-code-bot.private-key.pem').read_text()

SCHEDULER_HOST = env('SCHEDULER_HOST')

GH_TOKEN = env('GH_TOKEN')

SENTRY_KEY = env('SENTRY_KEY', str, default=None)

ENVIRONMENT = env('ENVIRONMENT', str, default='development')

if SENTRY_KEY:
    sentry_sdk.init(
        environment=ENVIRONMENT,
        dsn=f'https://{SENTRY_KEY}@o1351389.ingest.us.sentry.io/4508574747656192',
        traces_sample_rate=1.0,
        _experiments={
            'continuous_profiling_auto_start': True,
        },
        ignore_errors=[DisallowedHost],
    )

STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'main': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
RABBITMQ_HOST = env('RABBITMQ_HOST', str, default='localhost')
RABBITMQ_PORT = env('RABBITMQ_PORT', int, default=5672)
RABBITMQ_USER = env('RABBITMQ_USER', str, default='admin')
RABBITMQ_PASS = env('RABBITMQ_PASS', str, default='admin')
RABBITMQ_VHOST = env('RABBITMQ_VHOST', str, default='revive_code_bot')
REPO_PROCESS_ORDER_QUEUE_NAME = 'revive_code_bot.ordered_repos'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'main': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

ADMIN_SECRET_PATH = env('ADMIN_SECRET_PATH', str, default='')

CRONIQ_API_KEY = env('CRONIQ_API_KEY', str, default='fake')
CRONIQ_DOMAIN = env('CRONIQ_DOMAIN', str, default='https://croniq.ilaletdinov.ru')
