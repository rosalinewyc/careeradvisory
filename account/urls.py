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
    url(r'^recommendjob/$', views.recommendjob, name='recommendjob'),
    url(r'^modulesearch/$', views.modulesearch, name='modulesearch'),
    url(r'^modsearch/$', views.modsearch, name='modsearch'),
    url(r'^userprofile/$', views.userprofile, name='userprofile'),
    url(r'^personalinterest/$', views.personalinterest, name='personalinterest'),
    url(r'^interestinput/$', views.interestinput, name='interestinput'),
    url(r'^retrievestudentinterest/$', views.retrievestudentinterest, name='retrievestudentinterest'),
    url(r'^getstudentinterest/$', views.getstudentinterest, name='getstudentinterest'),
    url(r'^transitionjobpage/$', views.transitionjobpage, name='transitionjobpage'),
    url(r'^courserequirement/$', views.courserequirement, name='courserequirement'),
    url(r'^modcompare/$', views.modcompare, name='modcompare'),
    url(r'^specialisedropdown/$', views.specialisedropdown, name='specialisedropdown'),
    url(r'^specialisechoice/$', views.specialisechoice, name='specialisechoice'),
    url(r'^personalinterestsectordropdown/$', views.personalinterestsectordropdown, name='personalinterestsectordropdown'),
    url(r'^getcoursespecialization/$', views.getcoursespecialization, name='getcoursespecialization'),

]