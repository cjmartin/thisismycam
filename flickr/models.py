from django.db import models

from cameras.models import Camera

class FlickrUser(models.Model):
    nsid = models.CharField(max_length=255, unique=True, primary_key=True)
    username = models.CharField(max_length=255)
    realname = models.CharField(max_length=255, null=True, blank=True)
    path_alias = models.CharField(max_length=255, null=True, blank=True)
    iconserver = models.IntegerField()
    iconfarm = models.IntegerField()
    count_photos_processed = models.IntegerField(null=True, blank=True)
    date_last_photo_update = models.IntegerField(null=True, blank=True)
    
    cameras = models.ManyToManyField(Camera, through='FlickrUserCamera')
    
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.username
        
class FlickrUserCamera(models.Model):
    flickr_user = models.ForeignKey(FlickrUser)
    camera = models.ForeignKey(Camera)
    count_photos = models.IntegerField()

    date_update = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s + %s" % (self.flickr_user.username, self.camera.name)