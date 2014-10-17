from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
	url(r'dropbox/$', views.webhook_dropbox, name= 'webhook-dropbox'),
	url(r'crowdcafe/goldcontrol/$', views.webhook_crowdcafe_goldcontrol, name= 'webhook-crowdcafe-goldcontrol'),
	url(r'getMediaLink/(?P<uid>\d+)/$', views.getMediaLink, name= 'webhook-image-directlink'),

)
