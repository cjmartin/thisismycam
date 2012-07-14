from django.db import models

class FlickrUser(models.Model):
    nsid = models.CharField(max_length=255, unique=True, primary_key=True)
    username = models.CharField(max_length=255)
    realname = models.CharField(max_length=255, null=True, blank=True)
    path_alias = models.CharField(max_length=255, null=True, blank=True)
    iconserver = models.IntegerField()
    iconfarm = models.IntegerField()
    count_photos_processed = models.IntegerField(null=True, blank=True)
    date_last_photo_update = models.IntegerField(null=True, blank=True)
    
#    cameras = models.ManyToManyField(Camera, through='FlickrUserCamera')
    
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.username