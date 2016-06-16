# -*- coding: utf-8 -*-

from flask import Flask
from importlib import import_module


app = Flask(__name__)
app.config.from_envvar("FLASK_CONF")


import_module('urls')
