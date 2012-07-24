from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'flickr.views.user', name='flickr-user'),
    url(r'^cameras/(?P<camera_slug>[\w-]+)', 'flickr.views.user_camera', name='flickr-user-camera'),
)