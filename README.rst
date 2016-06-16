##############
Multiuser Blog
##############

Installation
============

Google App Engine
-----------------

Install the `App Engine Python SDK <https://developers.google.com/appengine/downloads>`_.
See the README file for directions. You'll need python 2.7 and `pip 1.4 or later <http://www.pip-installer.org/en/latest/installing.html>`_ installed too.

Project Dependencies
---------------------

Install dependencies in the project's lib directory. Note that App Engine can only import libraries from inside your project directory.

.. code:: sh

    $ pip install -r requirements.txt -t lib


Running Locally
===============

Local Configuration File
------------------------

You'll need to configure and register a ``SECRET_KEY`` for the Flask app. This will be done in ``priv.cfg``; see `priv.cfg.example <./priv.cfg.example>`_) for a guide on how to set it up.

SECRET_KEY
    Random key used for app security (sessions, etc.)

Run server
----------

.. code:: sh

    $ dev_appserver.py .

Visit the application at http://localhost:8080.

See `the Google App Engine development server documentation <https://developers.google.com/appengine/docs/python/tools/devserver>`_ for more options when running ``dev_appserver``.


Licensing
=========
See `LICENSE <./LICENSE>`_.


:Authors:
    Eddo Williams Hintoso
