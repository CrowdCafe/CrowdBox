from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
	url(r'webhook_dropbox/$', views.webhook_dropbox, name= 'imagesource-webhook'),
	#url(r'webhook_crowdcafe/$', views.webhook_crowdcafe, name= 'imagesource-crowdcafe'),
	url(r'getMediaLink/(?P<uid>\d+)/$', views.getMediaLink, name= 'imagesource-get-image-link'),
)
