from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'organizers/mail/$', 'fns_admin.views.mail_organizers'),
    url(r'organizers/mail/done/$', 'fns_admin.views.mail_organizers_done'),
    url(r'lots/review/(?P<borough>\D+)/$', 'fns_admin.views.review_lots'),
)
