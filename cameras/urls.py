from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'cameras.views.index', name='index'),
    url(r'^([\w-]+)', 'cameras.views.camera', name='user'),
)