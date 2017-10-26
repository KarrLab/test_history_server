""" WSGI configuration
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-01
:Copyright: 2016, Karr Lab
:License: MIT
"""

import sys, os

# Use custom version of python
INTERP = "/home/karrlab_tests/opt/python-3.6.3/bin/python3"
if os.path.isfile(INTERP) and sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Instantiate application
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_history_server.site.settings")
application = get_wsgi_application()
