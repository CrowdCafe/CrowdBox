from django.conf.urls import patterns, include, url

import views


urlpatterns = patterns('',
	url(r'^$', views.welcome, name= 'welcome'),
    url(r'^logout/$', views.logout_user, name= 'logout'),
	
	
)
