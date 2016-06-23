# -*- coding: utf-8 -*-

from flask import Flask
from importlib import import_module

from settings import INSTALLED_APPS


app = Flask(__name__)
app.config.from_envvar("FLASK_CONF")


# register applications
for installed_app in INSTALLED_APPS:
    mod = import_module(installed_app)
    try:
        url_prefix = mod.URL_PREFIX
    except AttributeError:
        app.register_blueprint(mod.api.blueprint)
    else:
        app.register_blueprint(mod.api.blueprint,
                               url_prefix='/api/{}'.format(url_prefix))

# error handlers
import_module('errors')
