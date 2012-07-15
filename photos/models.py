from django.db import models

from cameras.models import Camera
from cameras.models import Make
from cameras.models import Category

from flickr.models import FlickrPlace

class Photo(models.Model):
    photo_id = models.BigIntegerField(unique=True, primary_key=True)
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
    comments_count = models.IntegerField(null=True, blank=True)
    faves_count = models.IntegerField(null=True, blank=True)
    has_geo =  models.BooleanField(default=0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    accuracy = models.IntegerField(null=True, blank=True)
    context = models.IntegerField(null=True, blank=True)
    flickr_place = models.ForeignKey(FlickrPlace, null=True, blank=True)
    
    def __unicode__(self):
        return "%s + %s" % (self.photo_id, self.camera.name)
        
    def flickr_photo_page(self):
        if self.path_alias:
            identifier = self.path_alias
        else:
            identifier = self.owner_nsid
            
        return "http://flickr.com/photos/%s/%s" % (identifier, self.photo_id)
        
    def square_150_url(self):
        return "http://farm%s.staticflickr.com/%s/%s_%s_q.jpg" % (self.farm, self.server, self.photo_id, self.secret)
        
    def square_75_url(self):
        return "http://farm%s.staticflickr.com/%s/%s_%s_s.jpg" % (self.farm, self.server, self.photo_id, self.secret)
