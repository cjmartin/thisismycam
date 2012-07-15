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
    amazon_url = models.CharField(max_length=255, null=True, blank=True)
    amazon_item_response = models.TextField(null=True, blank=True)
    amazon_image_response = models.TextField(null=True, blank=True)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    large_photo_url = models.CharField(max_length=255, null=True, blank=True)
    medium_photo_url = models.CharField(max_length=255, null=True, blank=True)
    small_photo_url = models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
