# -*- coding: utf-8 -*-
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# CSRF_TRUSTED_ORIGINS = ['192.168.0.173','dtc-test.fimm.fi']
# ALLOWED_HOSTS = ['192.168.0.173','localhost','dtc-test.fimm.fi']
ALLOWED_HOSTS = ['*']
ADMINS = [('Zaid Alam', 'zaid.alam@helsinki.fi')]
SERVER_EMAIL = 'zaidimtiaz@gmail.com'
CSRF_COOKIE_SECURE = False
SITE_ID = 2

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
                'options': '-c search_path=chembl22'
            },
        'NAME': 'testdb',
        'USER': 'fimm',
        'PASSWORD': 'pxqgBsFLTwTzc',
        'HOST': 'localhost',
        'PORT': ''
        # 'HOST': '192.168.0.173',
        # 'PORT': '5432'
    }
}