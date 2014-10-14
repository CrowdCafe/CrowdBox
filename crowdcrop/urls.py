from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('general.urls')),

    url(r'account/', include('social_auth.urls')),
    url(r'user/', include('account.urls')),
    url(r'marble3d/', include('marble3d.urls')),
    url(r'imagesource/', include('imagesource.urls')),

    url(r'admin/', include(admin.site.urls)),
)