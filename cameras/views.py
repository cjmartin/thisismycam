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
        flickr_user = user.flickr_user
        
        return redirect('flickr-user', user_slug=flickr_user.slug)