from django.contrib import admin

from flickr.models import FlickrUser
from flickr.models import FlickrUserCamera

class FlickrUserCameraInline(admin.TabularInline):
    model = FlickrUserCamera
    extra = 0
    
class FlickrUserAdmin(admin.ModelAdmin):
    inlines = [
        FlickrUserCameraInline
    ]

admin.site.register(FlickrUser, FlickrUserAdmin)
#admin.site.register(FlickrUser)
admin.site.register(FlickrUserCamera)