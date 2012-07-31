from django.db import models
from django.db.models.signals import post_save
from django.utils import simplejson

from social_auth.signals import pre_update
from social_auth.backends.contrib.flickr import FlickrBackend

import flickr_api
from flickr_api.api import flickr

from django.contrib.auth.models import User
from flickr.models import FlickrUser

from flickr.tasks import process_new_flickr_user

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Flickr
    flickr_nsid = models.CharField(max_length=255, null=True, blank=True)
    flickr_username = models.CharField(max_length=255, null=True, blank=True)
    flickr_fullname = models.CharField(max_length=255, null=True, blank=True)
    flickr_oauth_token = models.CharField(max_length=255, null=True, blank=True)
    flickr_oauth_token_secret = models.CharField(max_length=255, null=True, blank=True)
    flickr_user = models.OneToOneField(FlickrUser, null=True, blank=True)
    
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.user.username
        
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
post_save.connect(create_user_profile, sender=User)

def flickr_extra_values(sender, user, response, details, **kwargs):
    from urlparse import parse_qs
    access_token = parse_qs(response['access_token'])
    
    a = flickr_api.AuthHandler(access_token_key = str(access_token['oauth_token'][0]), access_token_secret = str(access_token['oauth_token_secret'][0]))
    flickr_api.set_auth_handler(a)

    rsp = flickr.people.getInfo(user_id=response['id'],format="json",nojsoncallback="true")
    json = simplejson.loads(rsp)
    
    if json and json['stat'] == "ok":
        api_user = json['person']
        
        flickr_user, created = FlickrUser.objects.get_or_create(
            nsid = response['id'],
            defaults = {
                'username': api_user['username']['_content'],
                'realname': api_user['realname']['_content'],
                'path_alias': api_user['path_alias'],
                'iconserver': api_user['iconserver'],
                'iconfarm': api_user['iconfarm'],
            }
        )
        
        if created:
            process_new_flickr_user.delay(flickr_user.nsid)
            
        else:
            flickr_user.username = api_user['username']['_content']
            flickr_user.realname = api_user['realname']['_content']
            flickr_user.path_alias = api_user['path_alias']
            flickr_user.iconserver = api_user['iconserver']
            flickr_user.iconfarm = api_user['iconfarm']
    
            flickr_user.save()
    
    try:
      profile = user.get_profile()
    except:
      profile = UserProfile.objects.create(user = user)
      
    profile.flickr_nsid = response['id']
    profile.flickr_username = response['username']
    profile.flickr_fullname = response['fullname']
    profile.flickr_oauth_token = access_token['oauth_token'][0]
    profile.flickr_oauth_token_secret = access_token['oauth_token_secret'][0]
    if flickr_user:
        profile.flickr_user = flickr_user
    
    profile.save()
    return True
    
pre_update.connect(flickr_extra_values, sender=FlickrBackend)