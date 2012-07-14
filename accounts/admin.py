from django.contrib import admin

from accounts.models import UserProfile
from accounts.models import FlickrContact
    
class FlickrContactInline(admin.TabularInline):
    model = FlickrContact
    extra = 0
    
class UserProfileAdmin(admin.ModelAdmin):
    inlines = [
        FlickrContactInline
    ]

#admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserProfile)
admin.site.register(FlickrContact)