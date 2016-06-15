# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for

from application import app


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return redirect(url_for('blog'))


@app.route('/blog')
def blog():
    """Return a friendly HTTP greeting."""
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
