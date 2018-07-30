# -*- coding: utf-8 -*-
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
                'options': '-c search_path=chembl22'
            },
        'NAME': 'compounds_20',
        'USER': 'fimm',
        'PASSWORD': 'pxqgBsFLTwTzc',
        # 'HOST': 'localhost',
        # 'PORT': ''
        'HOST': '192.168.0.173',
        'PORT': '5432'
    }
}