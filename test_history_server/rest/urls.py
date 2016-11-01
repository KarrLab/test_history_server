""" REST API URL patterns
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-01
:Copyright: 2016, Karr Lab
:License: MIT
"""

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^submit_report/*$', views.submit_report),
    ]
