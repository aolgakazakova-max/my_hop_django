from .base import *  # noqa: F403

ALLOWED_HOSTS = ['example.com']
DEBUG = False

# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),  # noqa: F405
        'USER': os.getenv('POSTGRES_USER'),  # noqa: F405
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),  # noqa: F405
        'HOST': os.getenv('POSTGRES_HOST'),  # noqa: F405
        'PORT': os.getenv('POSTGRES_PORT'),  # noqa: F405
    }
}
