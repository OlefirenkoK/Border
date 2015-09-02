from django.conf.urls import include, url

urlpatterns = [

    url(r'^addNew/$', 'morgut.views.addNew'),
    url(r'^tt_info/(?P<tt_id>\d+)/$', 'morgut.views.tt_info'),
    url(r'^tt_info/(?P<tt_id>\d+)/history/(?P<page_number>\d+)/$', 'morgut.views.tt_history'),
    url(r'^update_item/(?P<tt_id>\d+)/$', 'morgut.views.update_item'),
    url(r'^downloadCKB/(?P<tt_id>\d+)/$', 'morgut.views.download_file'),
    url(r'^migrate_tt/(?P<tt_id>\d+)/$', 'morgut.views.migrate_tt'),
    url(r'^verificate_tt/$', 'morgut.views.verificate_tt'),
    url(r'^get_item/$', 'morgut.views.get_item'),
    url(r'^update_tt/$', 'morgut.views.update_tt'),
    url(r'^getICWW/$', 'morgut.views.get_ICWW'),
    url(r'^', 'morgut.views.board'),

]