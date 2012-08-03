from django.contrib import admin

from cameras.models import Camera
from cameras.models import Make
from cameras.models import Category

class CameraAdmin(admin.ModelAdmin):
    search_fields = ['name']
    
    def change_view(self, request, object_id, extra_context=None):
        camera = Camera.objects.get(id = int(object_id))
        aws_items = get_aws_info(camera)
                
        extra_context = {
            'camera': camera,
            'aws_items': aws_items,
        }
        return super(CameraAdmin, self).change_view(request, object_id, extra_context=extra_context)

admin.site.register(Camera, CameraAdmin)
admin.site.register(Make)
admin.site.register(Category)