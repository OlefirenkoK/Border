from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import JsonResponse, HttpResponse, Http404

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('loginsys.urls')),
    url(r'^list/', include('morgut.urls')),
    url(r'^', include('morgut.urls')),

)
