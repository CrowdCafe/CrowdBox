from django.conf.urls import patterns,url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^mine/$',TemplateView.as_view(template_name='welcome.html'), name='website-welcome'),
    url(r'^mine/$',TemplateView.as_view(template_name='info.html'), name='website-info'),

)