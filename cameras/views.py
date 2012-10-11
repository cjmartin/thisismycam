from django.conf import settings
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.utils import simplejson
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from cameras.models import Camera
from cameras.models import Category

from flickr.models import FlickrUserCamera

import urllib2

def camera(request, camera_slug):
    camera = get_object_or_404(Camera, slug=camera_slug)
    user_cameras = FlickrUserCamera.objects.filter(camera = camera)
    
    return HttpResponse(camera.name)

@csrf_exempt
def categorizer(request):
    if request.POST:
        camera_id = request.POST.get('camera_id',False)
        category_id = request.POST.get('category_id',False)
        
        camera = Camera.objects.get(pk=camera_id)
        category = Category.objects.get(pk=category_id)
        camera.category.add(category)
        
        if request.is_ajax():
            data = {
                'camera_id': camera.id,
                'category_id': category.id
            }
            return HttpResponse(simplejson.dumps(data), mimetype='application/javascript')
            
    if request.user.is_authenticated() and request.user.has_perm('cameras.change_camera'):
        user = request.user.get_profile()
        
        #cameras = Camera.objects.filter(category__isnull=True).order_by('-avg_30_day')[:10]
        cameras = Camera.objects.filter(category__isnull=True).order_by('-count')[:20]
        for camera in cameras:
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
                    
        categories = Category.objects.all()
        
        data = {
            'user': user,
            'cameras': cameras,
            'categories': categories
        }
        return render_to_response('admin/cameras/categorizer.html', data)