from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'setup$', views.setup, name='setup'),
    url(r'align$', views.align, name='align'),
    url(r'track$', views.track, name='track'),
    url(r'locations$', views.locations, name='locations'),
]