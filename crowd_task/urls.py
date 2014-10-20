from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'thumbnail/(?P<uid>\d+)/$', views.getThumbnail, name= 'task-thumbnail'),
    url(r'goldcontrol/$', views.controlGold, name= 'task-goldcontrol'),
    url(r'newjudgement/$', views.receiveNewJudgement, name= 'task-newjudgement'),
)
