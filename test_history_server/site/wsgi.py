import sys, os

INTERP = "/home/karrlab_tests/opt/python-3.5.2/bin/python"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_history_server.site.settings")
application = get_wsgi_application()
