from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'flickr.views.user', name='user'),
    url(r'^cameras/([\w-]+)', 'flickr.views.user_camera', name='flickr-user-camera'),
)