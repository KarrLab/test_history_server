""" URL patterns
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-01
:Copyright: 2016, Karr Lab
:License: MIT
"""

from django.conf.urls import include, url
import test_history_server.html.urls

urlpatterns = [
    url(r'^rest/', include('test_history_server.rest.urls')),
] + test_history_server.html.urls.urlpatterns
