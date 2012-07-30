from django.db import models

from cameras.models import Camera

class FlickrUser(models.Model):
    nsid = models.CharField(max_length=255, unique=True, primary_key=True)
    username = models.CharField(max_length=255)
    realname = models.CharField(max_length=255, null=True, blank=True)
    path_alias = models.CharField(max_length=255, unique=True, null=True, blank=True)
    iconserver = models.IntegerField()
    iconfarm = models.IntegerField()
    count_photos_processed = models.IntegerField(null=True, blank=True)
    date_last_photo_update = models.IntegerField(null=True, blank=True)
    
    cameras = models.ManyToManyField(Camera, through='FlickrUserCamera')
    contacts = models.ManyToManyField(FlickrUser, through='FlickrUserContact')
    
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.username
        
    def _get_slug(self):
        if self.path_alias:
            return self.path_alias
        else:
            return self.nsid
            
    slug = property(_get_slug)
    
    def _get_photos_url(self):
        return "http://flickr.com/photos/%s/" % self.slug
        
    photos_url = property(_get_photos_url)
    
class FlickrUserCamera(models.Model):
    flickr_user = models.ForeignKey(FlickrUser)
    camera = models.ForeignKey(Camera)
    count_photos = models.IntegerField(null=True, blank=True)
    date_first_taken = models.DateTimeField(null=True, blank=True)
    date_last_taken = models.DateTimeField(null=True, blank=True)
    date_first_upload = models.DateTimeField(null=True, blank=True)
    date_last_upload = models.DateTimeField(null=True, blank=True)
    first_taken_id = models.BigIntegerField(null=True, blank=True)
    last_taken_id = models.BigIntegerField(null=True, blank=True)
    first_upload_id = models.BigIntegerField(null=True, blank=True)
    last_upload_id = models.BigIntegerField(null=True, blank=True)
    comments_count = models.IntegerField(null=True, blank=True)
    faves_count = models.IntegerField(null=True, blank=True)

    date_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('flickr_user', 'camera')
        
    def __unicode__(self):
        return "%s + %s" % (self.flickr_user.username, self.camera.name)
        
class FlickrUserContact(models.Model):
    flickr_user = models.ForeignKey(FlickrUser)
    contact = models.ForeignKey(FlickrUser)
    
    class Meta:
        unique_together = ('flickr_user', 'contact')
        
    def __unicode__(self):
        return "%s + %s" % (self.flickr_user.username, self.contact.username)
        
class FlickrContactLookup(models.Model):
    flickr_user = models.ForeignKey(FlickrUser)
    nsid = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    iconserver = models.IntegerField()
    iconfarm = models.IntegerField()
    
    class Meta:
        unique_together = ('flickr_user', 'nsid')
        
    def __unicode__(self):
        return "%s + %s" % (self.flickr_user.username, self.username)