# -*- coding: utf-8 -*-

from importlib import import_module
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

APP_NAME = 'application'

DIRS = [
    'lib',
]

DIRS.append(APP_NAME)

for dir in DIRS:
    sys.path.insert(1, os.path.join(HERE, dir))

globals().update(import_module(APP_NAME).__dict__)
