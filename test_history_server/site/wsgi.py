""" WSGI configuration
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-01
:Copyright: 2016, Karr Lab
:License: MIT
"""

import sys, os

# Use python 3.5.2
INTERP = "/home/karrlab_tests/opt/python-3.5.2/bin/python"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

# Instantiate application
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_history_server.site.settings")
application = get_wsgi_application()
