from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^authenticate/$', views.authenticate, name='authenticate'),
    url(r'^logout/$', views.logout, name='logout'),

    # Admin
    url(r'^admin/index/$', views.admin_index, name='admin_index'),
    url(r'^bootstrap/$', views.admin_bootstrap, name='bootstrap'),

    # Student
    url(r'^courseplanner/$', views.courseplanner, name='courseplanner'),
    url(r'^recommendjob/$', views.recommendjob, name='recommendjob'),
    url(r'^modulesearch/$', views.modulesearch, name='modulesearch'),
    url(r'^userprofile/$', views.userprofile, name='userprofile'),
]