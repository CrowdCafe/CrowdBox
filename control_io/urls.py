from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
	url(r'dropbox/$', views.webhook_dropbox, name= 'io-dropbox'),
)
