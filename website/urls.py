from django.conf.urls import patterns,url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$',TemplateView.as_view(template_name='welcome.html'), name='website-welcome'),
    url(r'^info/$',TemplateView.as_view(template_name='info.html'), name='website-info'),

)