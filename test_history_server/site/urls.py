from django.conf.urls import include, url
import test_history_server.html.urls

urlpatterns = [
    url(r'^rest/', include('test_history_server.rest.urls')),
] + test_history_server.html.urls.urlpatterns 
