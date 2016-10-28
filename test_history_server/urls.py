from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('test_history_server.views',
    url(r'^$',                'index',         name='index'),
    url(r'^submit_report/*$', 'submit_report', name='submit_report'),
    url(r'^sitemap.xml$',     'sitemap',       name='sitemap'),
    url(r'^robots.txt$',      'robots',        name='robots'),
)
