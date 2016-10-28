import sys, os

INTERP = "/home/karrlab_tests/opt/python-2.7.12/bin/python"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())
sys.path.insert(0, '/home/karrlab_tests/opt/python-2.7.12/bin')
sys.path.insert(0, '/home/karrlab_tests/opt/python-2.7.12/lib/python2.7/site-packages/django')
sys.path.insert(0, '/')

os.environ['DJANGO_SETTINGS_MODULE'] = "test_history_server.settings"
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

from test_history_server import monitor
monitor.start(interval = 1.0)
