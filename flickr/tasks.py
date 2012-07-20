from django.conf import settings
from django.utils import simplejson
from django.db import IntegrityError
from django.db.models import F

from celery.task import task
from flickr_api.api import flickr

from flickr.models import FlickrUser
from flickr.models import FlickrUserCamera

from cameras.models import Camera

from photos.models import Photo

import logging
logger = logging.getLogger(__name__)

@task()
def flickr_user_fetch_photos_complete(results, nsid):
    flickr_user = FlickrUser.objects.get(nsid = nsid)

    last_photo = Photo.objects.latest('date_upload')
    flickr_user.date_last_photo_update = last_photo.date_upload
    
    # logger.info("Processed %s photos for %s" % (len(photos_processed), flickr_user.username))
    # if flickr_user.count_photos_processed:
    #     photos_processed = len(photos_processed) + flickr_user.count_photos_processed
    # 
    # flickr_user.count_photos_processed = photos_processed
    
    flickr_user.save()
    
    # logger.info("Fetch for %s complete. That was fun!" % (flickr_user.username))
    logger.info("Fetch complete. That was fun!")
    return

@task()
def update_flickr_user_camera(photo_id, nsid):
    if photo_id:
        flickr_user = FlickrUser.objects.get(pk = nsid)
        photo = Photo.objects.get(pk = photo_id)
        camera = photo.camera
    
        logger.info("Updating flickr_user (%s) with camera (%s)." % (flickr_user, camera))
        
        try:
            flickr_user_camera, create = FlickrUserCamera.objects.get_or_create(
                camera = camera,
                flickr_user = flickr_user,
                defaults = {
                    'count_photos': 1,
                    'comments_count': photo.comments_count,
                    'faves_count': photo.faves_count,
                    'date_last_taken': photo.date_taken,
                    'date_last_upload': photo.date_upload,
                }
            )
            
        except IntegrityError:
            logger.warning("FlickrUserCamera %s + %s already exists, but we're trying to add it again. Rescheduling task." % (flickr_user, camera))
            raise update_flickr_user_camera.retry(countdown=5)
            
        if not create:
            logger.info("We've seen this camera (%s) for this user before, updating counts." % (camera))
            
            # Update counts
            FlickrUserCamera.objects.filter(pk=flickr_user_camera.pk).update(count_photos=F('count_photos')+1)
            
            if photo.comments_count:
                FlickrUserCamera.objects.filter(pk=flickr_user_camera.pk).update(comments_count=F('comments_count')+int(photo.comments_count))
                
            if photo.faves_count:
                FlickrUserCamera.objects.filter(pk=flickr_user_camera.pk).update(faves_count=F('faves_count')+int(photo.faves_count))
                
        return
        
    return