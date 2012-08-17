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
    count_photos = models.IntegerField(default=0)
    count_cameras = models.IntegerField(default=0)
    initial_fetch_completed = models.BooleanField(default=0)
    
    cameras = models.ManyToManyField(Camera, through='FlickrUserCamera')
    contacts = models.ManyToManyField('self', through='FlickrUserContact', symmetrical=False)
    current_camera = models.ForeignKey('FlickrUserCamera', null=True, blank=True)
    
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
    
    def calculate_current_camera(self):
        from photos.models import Photo
        from datetime import timedelta
        import operator
        
        last_taken = Photo.objects.filter(owner_nsid=self.nsid).latest('date_taken')

        # Determine "The Cam"
        recent_photos = Photo.objects.filter(owner_nsid=self.nsid, date_taken__gt=(last_taken.date_taken - timedelta(days=30)))
        recent_cameras = {}

        for photo in recent_photos:
            try:
                recent_cameras[photo.camera.id] += 1
            except KeyError:
                recent_cameras[photo.camera.id] = 1
                
        camera_id = max(recent_cameras.iteritems(), key=operator.itemgetter(1))[0]
        
        return self.flickrusercamera_set.get(camera=camera_id)
            
    
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
    flickr_user = models.ForeignKey(FlickrUser, related_name='+')
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