from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'(?P<camera_slug>[\w-]+)', 'cameras.views.camera', name='camera'),
)