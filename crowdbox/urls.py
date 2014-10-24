from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('website.urls')),

    url(r'account/', include('social_auth.urls')),
    url(r'user/', include('account.urls')),

    url(r'io/', include('crowd_io.urls')),
    url(r'task/', include('crowd_task.urls')),

    url(r'admin/', include(admin.site.urls)),
)