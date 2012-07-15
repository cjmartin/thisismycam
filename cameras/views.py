from django.conf import settings
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.utils import simplejson

from cameras.models import Camera

def index(request):
    if not request.user.is_authenticated():
        data = {
            'user': None,
        }
        return render_to_response('cameras/index.html', data)
    else:
        user = request.user.get_profile()
        user_cameras = user.flickr_user.cameras.all()
        for camera in user_cameras:
            if camera.amazon_image_response:
                camera.amazon_image_response = simplejson.loads(camera.amazon_image_response)
                
            if camera.amazon_item_response:
                camera.amazon_item_response = simplejson.loads(camera.amazon_item_response)
                if not camera.amazon_url:
                    # Clean up and add the item url
                    url = urllib2.unquote(camera.amazon_item_response['DetailPageURL'])
                    split_url = url.split('?')
                    pretty_url = split_url[0] + "?tag=" + settings.AWS_ASSOCIATE_TAG
                    camera.amazon_url = pretty_url
        
        data = {
            'user': user,
            'user_cameras': user_cameras,
        }
    
        return render_to_response('cameras/user_index.html', data)