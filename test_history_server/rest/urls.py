from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^submit_report/*$', views.submit_report),
    ]
