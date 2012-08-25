from django.contrib import admin

from flickr.models import FlickrUser
from flickr.models import FlickrUserCamera
from flickr.models import FlickrUserContact
from flickr.models import FlickrContactLookup

class FlickrUserCameraInline(admin.TabularInline):
    model = FlickrUserCamera
    extra = 0
    
class FlickrUserAdmin(admin.ModelAdmin):
    search_fields = ['username']
    list_display = ('username', 'realname', 'nsid', 'path_alias', 'count_cameras', 'count_contacts', 'count_photos', 'count_photos_processed', 'date_last_photo_update', 'date_create')
    
    inlines = [
        FlickrUserCameraInline
    ]

admin.site.register(FlickrUser, FlickrUserAdmin)
admin.site.register(FlickrUserCamera)
admin.site.register(FlickrUserContact)
admin.site.register(FlickrContactLookup)