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
        
    def photos_url(self):
        if self.path_alias:
            identifier = self.path_alias
        else:
            identifier = self.nsid
            
        return "http://flickr.com/photos/%s/" % identifier
        
class FlickrUserCamera(models.Model):
    flickr_user = models.ForeignKey(FlickrUser)
    camera = models.ForeignKey(Camera)
    count_photos = models.IntegerField()
    date_first_taken = models.DateTimeField()
    date_last_taken = models.DateTimeField()
    date_first_upload = models.DateTimeField()
    date_last_upload = models.DateTimeField()
    first_taken_id = models.BigIntegerField()
    last_taken_id = models.BigIntegerField()
    first_upload_id = models.BigIntegerField()
    last_upload_id = models.BigIntegerField()
    comments_count = models.IntegerField(null=True, blank=True)
    faves_count = models.IntegerField(null=True, blank=True)

    date_update = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s + %s" % (self.flickr_user.username, self.camera.name)
        
class FlickrPlace(models.Model):
    place_id = models.CharField(max_length=255, unique=True, primary_key=True)
    woeid = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    place_url = models.CharField(max_length=255)
    place_type = models.CharField(max_length=255)
    place_type_id = models.IntegerField()
    timezone = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    neighbourhood_place_id = models.CharField(max_length=255, null=True, blank=True)
    neighbourhood_woeid = models.IntegerField(null=True, blank=True)
    neighbourhood_latitude = models.FloatField(null=True, blank=True)
    neighbourhood_longitude = models.FloatField(null=True, blank=True)
    neighbourhood_place_url = models.CharField(max_length=255, null=True, blank=True)
    neighbourhood_name = models.CharField(max_length=255, null=True, blank=True)
    locality_place_id = models.CharField(max_length=255, null=True, blank=True)
    locality_woeid = models.IntegerField(null=True, blank=True)
    locality_latitude = models.FloatField(null=True, blank=True)
    locality_longitude = models.FloatField(null=True, blank=True)
    locality_place_url = models.CharField(max_length=255, null=True, blank=True)
    locality_name = models.CharField(max_length=255, null=True, blank=True)
    county_place_id = models.CharField(max_length=255, null=True, blank=True)
    county_woeid = models.IntegerField(null=True, blank=True)
    county_latitude = models.FloatField(null=True, blank=True)
    county_longitude = models.FloatField(null=True, blank=True)
    county_place_url = models.CharField(max_length=255, null=True, blank=True)
    county_name = models.CharField(max_length=255, null=True, blank=True)
    region_place_id = models.CharField(max_length=255, null=True, blank=True)
    region_woeid = models.IntegerField(null=True, blank=True)
    region_latitude = models.FloatField(null=True, blank=True)
    region_longitude = models.FloatField(null=True, blank=True)
    region_place_url = models.CharField(max_length=255, null=True, blank=True)
    region_name = models.CharField(max_length=255, null=True, blank=True)
    country_place_id = models.CharField(max_length=255, null=True, blank=True)
    country_woeid = models.IntegerField(null=True, blank=True)
    country_latitude = models.FloatField(null=True, blank=True)
    country_longitude = models.FloatField(null=True, blank=True)
    country_place_url = models.CharField(max_length=255, null=True, blank=True)
    country_name = models.CharField(max_length=255, null=True, blank=True) 