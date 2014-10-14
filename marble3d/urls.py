from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

import views


urlpatterns = patterns('',
                       # Home page
                       # --------------------------------------------------------------------------------------
                       # Quality control
                       url(r'judgements/control/$', views.assesJudgementAgainstGold, name='marble3d-judgement-control'),
                       # Results webhook
                       url(r'judgements/receive/$', views.receiveJudgement, name='marble3d-judgement-receive'),
                       # --------------------------------------------------------------------------------------
)
