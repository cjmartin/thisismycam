import os
import sys

path = '/home/cjmartin/djangoapps/thisismycam-prod'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'thisismycam.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
