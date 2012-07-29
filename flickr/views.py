from django.conf import settings
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.utils import simplejson

import re

from flickr.models import FlickrUser
from cameras.models import Camera
from photos.models import Photo

def index(request):
    if not request.user.is_authenticated():
        data = {
            'user': None,
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
    else:
        user = None
    
    user_cameras = flickr_user.flickrusercamera_set.order_by('-date_last_taken', '-count_photos')
    cameras_and_photos = load_photos_for_cameras(user_cameras, flickr_user.nsid)
    primary_camera = user_cameras[0]
    
    photos = Photo.objects.filter(camera = primary_camera.camera, owner_nsid = flickr_user.nsid).order_by('-date_taken')[:18]
    
    data = {
        'user': user,
        'flickr_user': flickr_user,
        'user_cameras': cameras_and_photos,
        'primary_camera': primary_camera,
        'photos': photos,
    }

    return render_to_response('flickr/user_index.html', data)
        
def user_camera(request, user_slug, camera_slug):
    flickr_user = get_user_by_slug(user_slug)
    camera = get_object_or_404(Camera, slug=camera_slug)
    
    if request.user.is_authenticated():
        user = request.user.get_profile()
    else:
        user = None
    
    user_cameras = flickr_user.flickrusercamera_set.order_by('-date_last_taken', '-count_photos')
    cameras_and_photos = load_photos_for_cameras(user_cameras, flickr_user.nsid)
    
    primary_camera = flickr_user.flickrusercamera_set.get(camera = camera)
    first_taken_photo = Photo.objects.get(photo_id = primary_camera.first_taken_id)
    
    photos = Photo.objects.filter(camera = primary_camera.camera, owner_nsid = flickr_user.nsid).order_by('-date_taken')[:18]
    
    data = {
        'user': user,
        'flickr_user': flickr_user,
        'user_cameras': cameras_and_photos,
        'primary_camera': primary_camera,
        'photos': photos,
    }

    return render_to_response('flickr/user_index.html', data)
    
def load_photos_for_cameras(user_cameras, nsid):
    cameras_and_photos = []
    for user_camera in user_cameras:
        if user_camera.camera.amazon_image_response:
            user_camera.camera.amazon_image_response = simplejson.loads(user_camera.camera.amazon_image_response)
            
        if user_camera.camera.amazon_item_response:
            user_camera.camera.amazon_item_response = simplejson.loads(user_camera.camera.amazon_item_response)
            if not user_camera.camera.amazon_url:
                # Clean up and add the item url
                url = urllib2.unquote(user_camera.camera.amazon_item_response['DetailPageURL'])
                split_url = url.split('?')
                pretty_url = split_url[0] + "?tag=" + settings.AWS_ASSOCIATE_TAG
                user_camera.camera.amazon_url = pretty_url
                
        photos = Photo.objects.filter(camera = user_camera.camera, owner_nsid = nsid).order_by('-date_taken')[:6]
        cameras_and_photos.append({'user_camera':user_camera, 'photos':photos})
        
    return cameras_and_photos
    
def get_user_by_slug(user_slug):
    # NSID
    if re.search('(@N\d+)$', user_slug):
        return get_object_or_404(FlickrUser, nsid=user_slug)
    else:
        return get_object_or_404(FlickrUser, path_alias=user_slug)
        