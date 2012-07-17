from django.conf import settings
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.utils import simplejson

from cameras.models import Camera
from photos.models import Photo

def index(request):
    if not request.user.is_authenticated():
        data = {
            'user': None,
        }
        return render_to_response('cameras/index.html', data)
    else:
        user = request.user.get_profile()
        # user_cameras = user.flickr_user.cameras.all()
        user_cameras = user.flickr_user.flickrusercamera_set.order_by('-date_last_taken', '-count_photos')
        
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
                    
            photos = Photo.objects.filter(camera = user_camera.camera, owner_nsid = user.flickr_nsid).order_by('date_create')[:6]
            cameras_and_photos.append({'user_camera':user_camera, 'photos':photos})
        
        primary_camera = user_cameras[0]
        first_taken_photo = Photo.objects.get(photo_id = primary_camera.first_taken_id)
        
        photos = Photo.objects.filter(camera = primary_camera.camera, owner_nsid = user.flickr_nsid).order_by('date_create')[:18]
        
        data = {
            'user': user,
            'user_cameras': cameras_and_photos,
            'primary_camera': primary_camera,
            'first_taken_photo': first_taken_photo,
            'photos': photos,
        }
    
        return render_to_response('cameras/user_index.html', data)
        
def camera(request, slug):
    if not request.user.is_authenticated():
        data = {
            'user': None,
        }
        return render_to_response('cameras/index.html', data)
    else:
        user = request.user.get_profile()
        camera = get_object_or_404(Camera, slug=slug)
        
        # user_cameras = user.flickr_user.cameras.all()
        user_cameras = user.flickr_user.flickrusercamera_set.order_by('-date_last_taken', '-count_photos')
        
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
                    
            photos = Photo.objects.filter(camera = user_camera.camera, owner_nsid = user.flickr_nsid).order_by('date_taken')[:6]
            cameras_and_photos.append({'user_camera':user_camera, 'photos':photos})
        
        primary_camera = user.flickr_user.flickrusercamera_set.get(camera = camera)
        first_taken_photo = Photo.objects.get(photo_id = primary_camera.first_taken_id)
        
        photos = Photo.objects.filter(camera = primary_camera.camera, owner_nsid = user.flickr_nsid).order_by('date_taken')[:18]
        
        data = {
            'user': user,
            'user_cameras': cameras_and_photos,
            'primary_camera': primary_camera,
            'first_taken_photo': first_taken_photo,
            'photos': photos,
        }
    
        return render_to_response('cameras/user_index.html', data)