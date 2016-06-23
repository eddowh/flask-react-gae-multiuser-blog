# -*- coding: utf-8 -*-

from importlib import import_module
import os
import sys


BASE_PATH = os.path.dirname(os.path.abspath(__file__))

APP_NAME = 'server'
SYS_DIRS = [
    'lib',
]

# add directories to sys path
for dir in SYS_DIRS + [APP_NAME]:
    sys.path.insert(1, os.path.join(BASE_PATH, dir))

# register flask configuration environment variable
SETTINGS_FILEPATH = os.path.join(BASE_PATH, 'priv.cfg')
os.environ.setdefault("FLASK_CONF", SETTINGS_FILEPATH)

# for starting GAE
globals().update(import_module(APP_NAME).__dict__)
