from django.db import models

class Make(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    count = models.IntegerField()
    
    def __unicode__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __unicode__(self):
        return self.name

class Camera(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    make = models.ForeignKey('Make', null=True, blank=True)
    exif_make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255)
    exif_model = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    category = models.ManyToManyField('Category')
    count = models.IntegerField()
    count_photos = models.IntegerField()
    amazon_url = models.CharField(max_length=255, null=True, blank=True)
    amazon_item_response = models.TextField(null=True, blank=True)
    amazon_image_response = models.TextField(null=True, blank=True)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    large_photo_url = models.CharField(max_length=255, null=True, blank=True)
    large_photo_width = models.IntegerField()
    large_photo_height = models.IntegerField()
    medium_photo_url = models.CharField(max_length=255, null=True, blank=True)
    medium_photo_width = models.IntegerField()
    medium_photo_height = models.IntegerField()
    small_photo_url = models.CharField(max_length=255, null=True, blank=True)
    small_photo_width = models.IntegerField()
    small_photo_height = models.IntegerField()
    
    def __unicode__(self):
        return self.name
        
    def _get_large_orientation(self):
        if self.large_photo_width == self.large_photo_height:
            return "square"
        elif self.large_photo_width > self.large_photo_height:
            return "landscape"
        else:
            return "portrait"

    large_orientation = property(_get_large_orientation)
    
    def _get_medium_orientation(self):
        if self.medium_photo_width == self.medium_photo_height:
            return "square"
        elif self.medium_photo_width > self.medium_photo_height:
            return "landscape"
        else:
            return "portrait"

    medium_orientation = property(_get_medium_orientation)
    
    def _get_small_orientation(self):
        if self.small_photo_width == self.small_photo_height:
            return "square"
        elif self.small_photo_width > self.small_photo_height:
            return "landscape"
        else:
            return "portrait"

    small_orientation = property(_get_small_orientation)