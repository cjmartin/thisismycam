from django.contrib import admin

from cameras.models import Camera
from cameras.models import Make
from cameras.models import Category

admin.site.register(Camera)
admin.site.register(Make)
admin.site.register(Category)