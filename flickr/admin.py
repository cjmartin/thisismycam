from django.contrib import admin

from flickr.models import FlickrUser
from flickr.models import FlickrUserCamera
# from flickr.models import FlickrPlace

class FlickrUserCameraInline(admin.TabularInline):
    model = FlickrUserCamera
    extra = 0
    
class FlickrUserAdmin(admin.ModelAdmin):
    inlines = [
        FlickrUserCameraInline
    ]

admin.site.register(FlickrUser, FlickrUserAdmin)
admin.site.register(FlickrUserCamera)
# admin.site.register(FlickrPlace)