from django.conf.urls import include, url

urlpatterns = [

    url(r'^logout/$', 'loginsys.views.logout'),
    url(r'^change_passwd/$', 'loginsys.views.change_passwd'),
    url(r'^login/$', 'loginsys.views.login'),

]