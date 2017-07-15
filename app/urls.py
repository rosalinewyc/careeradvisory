from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^bootstrap/$', views.adminbootstrap, name='bootstrap'),
    url(r'^courseplanner/$', views.courseplanner, name='courseplanner'),
    url(r'^recommendjob/$', views.recommendjob, name='recommendjob'),
    url(r'^modulesearch/$', views.modulesearch, name='modulesearch'),
    url(r'^userprofile/$', views.userprofile, name='userprofile'),
    url(r'^authenticate/$', views.authenticate, name='authenticate'),
]