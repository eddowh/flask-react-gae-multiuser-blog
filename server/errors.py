# -*- coding: utf-8 -*-

from flask import render_template

from application import app


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return '<h1>404: Not Found</h1>', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
