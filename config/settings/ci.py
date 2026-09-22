import os

from .base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'hop_django_luxe'),
        'USER': os.environ.get('POSTGRES_USER', 'hop_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'hop_password'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}