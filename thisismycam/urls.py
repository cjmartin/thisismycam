from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Index
    url(r'^$', 'flickr.views.index', name='index'),
    
    # Examples:
    # url(r'^$', 'thisismycam.views.home', name='home'),
    # url(r'^thisismycam/', include('thisismycam.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # Authentication
    url(r'', include('social_auth.urls')),
    url(r'^logout', 'accounts.views.logout_view', name='logout'),
    
    # User and User Camera Pages
    url(r'^(?P<user_slug>[\w@]+)/', include('flickr.urls')),
)
