from django.db import models

from cameras.models import Camera
from cameras.models import Make
from cameras.models import Category

class Photo(models.Model):
    photo_id = models.BigIntegerField()
    secret = models.CharField(max_length=255)
    server = models.IntegerField()
    farm = models.IntegerField()
    title = models.CharField(max_length=255, null=True, blank=True)
    license = models.IntegerField()
    media = models.CharField(max_length=255)
    owner_nsid = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    path_alias = models.CharField(max_length=255, null=True, blank=True)
    date_taken = models.DateTimeField()
    date_upload = models.DateTimeField()
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    camera = models.ForeignKey(Camera)
    camera_make = models.ForeignKey(Make, null=True, blank=True)
    
    def __unicode__(self):
        return "%s + %s" % (self.photo_id, self.camera.name)