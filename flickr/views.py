from django.conf import settings
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.utils import simplejson

import re
import hashlib

from flickr.models import FlickrUser
from flickr.models import FlickrUserCamera
from cameras.models import Camera
from photos.models import Photo

from cameras.tasks import add_aws_item_to_camera

def index(request):
    if not request.user.is_authenticated():
    	example_users = ['42982698@N00','36521956509@N01','51035718466@N01','95769700@N00','61091860@N00','43813659@N03']
        example_cams = []
        for nsid in example_users:
	        cam = FlickrUserCamera.objects.filter(flickr_user__nsid__exact=nsid).order_by('-date_last_taken', '-count_photos')[0]
	        example_cams.append(cam)
        
        data = {
            'example_cams': example_cams,
        }
        
        return render_to_response('flickr/index.html', data)

    else:
        user = request.user.get_profile()
        flickr_user = user.flickr_user

        return redirect('flickr-user', flickr_user.slug)

def user(request, user_slug):
    flickr_user = get_user_by_slug(user_slug)
    
    if request.user.is_authenticated():
        user = request.user.get_profile()
        if user.flickr_nsid == flickr_user.nsid:
            is_owner = True
        else:
            is_owner = False
    else:
        user = None
        is_owner = False
    
    data = {
        'user': user,
        'flickr_user': flickr_user,
        'is_owner': is_owner,
    }
    
    if request.is_ajax():
        cameras = flickr_user.cameras.all()[:8]
        count_cameras = flickr_user.cameras.count()
        
        data['user_contact'] = {'contact': flickr_user, 'count_cameras': count_cameras, 'cameras': cameras}
        return render_to_response('flickr/fragment_user_contact.html', data)
    
    shasum = hashlib.sha1()
    shasum.update(flickr_user.nsid + settings.PUSHY_SALT)
    pushy_channel = "%s_%s" % (flickr_user.nsid, shasum.hexdigest())
    
    data['pushy_url'] = settings.PUSHY_URL
    data['pushy_channel'] = pushy_channel
    
    user_cameras = flickr_user.flickrusercamera_set.order_by('-date_last_taken', '-count_photos')
    
    #Temp, add widths and heights to cameras if they don't exist
    # for user_camera in user_cameras:
    #     if not user_camera.camera.large_photo_width:
    #         add_aws_item_to_camera.delay(user_camera.camera.id)
    
    if user_cameras:        
        data['user_cameras'] = load_photos_for_cameras(user_cameras, flickr_user.nsid)
        data['primary_camera'] = user_cameras[0]
        data['photos'] = Photo.objects.filter(camera = user_cameras[0].camera, owner_nsid = flickr_user.nsid).order_by('-date_taken')[:18]
        
    data['contacts'] = load_cameras_for_contacts(flickr_user.contacts.filter(date_last_photo_update__isnull=False), 8)
    
    return render_to_response('flickr/user_index.html', data)
        
def user_camera(request, user_slug, camera_slug):
    flickr_user = get_user_by_slug(user_slug)
    camera = get_object_or_404(Camera, slug=camera_slug)
    user_camera = flickr_user.flickrusercamera_set.get(camera = camera)
    
    if request.user.is_authenticated():
        user = request.user.get_profile()
        if user.flickr_nsid == flickr_user.nsid:
            is_owner = True
        else:
            is_owner = False
    else:
        user = None
        is_owner = False
	
    data = {
        'user': user,
        'flickr_user': flickr_user,
        'is_owner': is_owner,
        'primary_camera': user_camera,
    }
    
    if request.is_ajax():
        photos = Photo.objects.filter(camera = user_camera.camera, owner_nsid = flickr_user.nsid).order_by('-date_taken')[:6]
        data['camera'] = {'user_camera': user_camera, 'photos': photos}
        
        return render_to_response('flickr/fragment_user_camera.html', data)
    
    if request.user.is_authenticated():
        data['user'] = request.user.get_profile()
    else:
        data['user'] = None
    
    data['photos'] = Photo.objects.filter(camera = camera, owner_nsid = flickr_user.nsid).order_by('-date_taken')[:18]
    
    user_cameras = flickr_user.flickrusercamera_set.order_by('-date_last_taken', '-count_photos')
    data['user_cameras'] = load_photos_for_cameras(user_cameras, flickr_user.nsid)
    
    return render_to_response('flickr/user_camera.html', data)
    
def load_photos_for_cameras(user_cameras, nsid):
    cameras_and_photos = []
    for user_camera in user_cameras:
        # if user_camera.camera.amazon_image_response:
        #             user_camera.camera.amazon_image_response = simplejson.loads(user_camera.camera.amazon_image_response)
        #             
        #         if user_camera.camera.amazon_item_response:
        #             user_camera.camera.amazon_item_response = simplejson.loads(user_camera.camera.amazon_item_response)
        #             if not user_camera.camera.amazon_url:
        #                 # Clean up and add the item url
        #                 url = urllib2.unquote(user_camera.camera.amazon_item_response['DetailPageURL'])
        #                 split_url = url.split('?')
        #                 pretty_url = split_url[0] + "?tag=" + settings.AWS_ASSOCIATE_TAG
        #                 user_camera.camera.amazon_url = pretty_url
        
        photos = Photo.objects.filter(camera = user_camera.camera, owner_nsid = nsid).order_by('-date_taken')[:6]
        cameras_and_photos.append({'user_camera': user_camera, 'photos': photos})
        
    return cameras_and_photos
    
def load_cameras_for_contacts(contacts, count=None):
    contacts_with_cameras = []
    for contact in contacts:
        if count:
            cameras = contact.cameras.all()[:count]
        else:
            cameras = contact.cameras.all()
            
        count_cameras = contact.cameras.count()
        
        contacts_with_cameras.append({'contact': contact, 'count_cameras': count_cameras, 'cameras': cameras})
        
    return contacts_with_cameras
    
def get_user_by_slug(user_slug):
    # NSID
    if re.search('(@N\d+)$', user_slug):
        return get_object_or_404(FlickrUser, nsid=user_slug)
    else:
        return get_object_or_404(FlickrUser, path_alias=user_slug)
        