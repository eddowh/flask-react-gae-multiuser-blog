# -*- coding: utf-8 -*-

from flask import Flask
from importlib import import_module


app = Flask(__name__)


import_module('urls')
