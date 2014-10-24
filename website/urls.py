from django.conf.urls import patterns
from django.views.generic import TemplateView

urlpatterns = patterns('',
    (r'^$', TemplateView.as_view(template_name='welcome.html', name='welcome')),
    (r'^info/$', TemplateView.as_view(template_name='info.html', name='info')),
)