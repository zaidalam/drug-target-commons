# -*- coding: utf-8 -*-
from .base import *
from django.core.exceptions import ImproperlyConfigured
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# CSRF_TRUSTED_ORIGINS = ['192.168.0.173','dtc-test.fimm.fi']
# ALLOWED_HOSTS = ['192.168.0.173','localhost','dtc-test.fimm.fi']
ALLOWED_HOSTS = ['*']
ADMINS = [('Zaid Alam', 'zaid.alam@helsinki.fi')]
SERVER_EMAIL = 'zaidimtiaz@gmail.com'
CSRF_COOKIE_SECURE = False
SITE_ID = 3


 
def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)
 
SECRET_KEY = get_env_variable('SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
                'options': '-c search_path=drugtargetcommons'
            },
        'NAME': 'compounds_20',
        'USER': 'fimm',
        'PASSWORD': 'pxqgBsFLTwTzc',
        'HOST': 'localhost',
        'PORT': ''
    }
}

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
CORS_ORIGIN_ALLOW_ALL = True

API_LIMIT_PER_PAGE = 20
