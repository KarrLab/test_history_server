""" HTML GUI URL patterns
:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-01
:Copyright: 2016, Karr Lab
:License: MIT
"""

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<owner>[^/]+)/*$', views.owner, name='owner'),
    url(r'^(?P<owner>[^/]+)/(?P<repo>[^/]+)/*$', views.repo, name='repo'),
    url(r'^(?P<owner>[^/]+)/(?P<repo>[^/]+)/(?P<build>[0-9]+)/*$', views.build, name='build'),
    url(r'^(?P<owner>[^/]+)/(?P<repo>[^/]+)/(?P<build>[0-9]+)/(?P<report>[^/]+)/*$', views.report, name='report'),
    url(r'^(?P<owner>[^/]+)/(?P<repo>[^/]+)/(?P<classname>[a-zA-Z0-9_\.]+)/*$', views.classname, name='classname'),
    url(r'^(?P<owner>[^/]+)/(?P<repo>[^/]+)/(?P<classname>[a-zA-Z0-9_\.]+)/(?P<case>[a-zA-Z0-9_\.]+)/*$', views.case, name='case'),

    url(r'^sitemap.xml$', views.sitemap),
    url(r'^robots.txt$', views.robots),
]
