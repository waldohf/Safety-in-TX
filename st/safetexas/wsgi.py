import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'safetexas.settings'

from django.core.handlers.wsgi import WSGIHandler

application = WSGIHandler()
