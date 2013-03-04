"""
WSGI config for mocs project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import sys

parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
site_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
django_path = '/usr/lib/python2.7/dist-packages/django'
paths = [site_path, parent_path, django_path]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mocs.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
'''
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    yield ' '.join(paths)
    yield ' '
    yield ' '.join(sys.path)
'''
