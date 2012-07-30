from django.conf import settings
from django.utils import simplejson
from django.db import IntegrityError

from django.db.models import F
from django.db.models import Sum

import calendar

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
    
    total_photos = 0
    cameras = flickr_user.cameras.all()
    
    for camera in cameras:
        logger.info("Updating camera %s for %s" % (camera, flickr_user))
        
        photos = Photo.objects.filter(camera=camera, owner_nsid=flickr_user.nsid)

        first_taken = photos.order_by('date_taken')[:1].get()
        last_taken = photos.latest('date_taken')
        first_upload = photos.order_by('date_upload')[:1].get()
        last_upload = photos.latest('date_upload')
        comments_count = photos.aggregate(Sum('comments_count'))
        faves_count = photos.aggregate(Sum('faves_count'))
        photos_count = photos.count()
                
        FlickrUserCamera.objects.filter(camera=camera, flickr_user=flickr_user).update(
            count_photos = photos_count,
            date_first_taken = first_taken.date_taken,
            first_taken_id = first_taken.photo_id,
            date_first_upload = first_upload.date_upload,
            first_upload_id = first_upload.photo_id,
            date_last_taken = last_taken.date_taken,
            last_taken_id = last_taken.photo_id,
            date_last_upload = last_upload.date_upload,
            last_upload_id = last_upload.photo_id,
            comments_count = comments_count['comments_count__sum'],
            faves_count = faves_count['faves_count__sum'],
        )
        
        total_photos = total_photos + photos_count
        
    last_photo = Photo.objects.filter(owner_nsid=flickr_user.nsid).latest('date_upload')
    
    flickr_user.date_last_photo_update = calendar.timegm(last_photo.date_upload.timetuple())
    flickr_user.count_photos_processed = total_photos
    flickr_user.save()
    
    logger.info("Fetch for %s complete. That was fun!" % (flickr_user.username))
    return

@task()
def update_flickr_user_camera(photo_id, nsid):
    if photo_id:
        flickr_user = FlickrUser.objects.get(pk = nsid)
        photo = Photo.objects.get(pk = photo_id)
        camera = photo.camera
    
        logger.info("Updating flickr_user (%s) with camera (%s)." % (flickr_user, camera))
        
        try:
            flickr_user_camera, created = FlickrUserCamera.objects.get_or_create(
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
            
        if created:
            Camera.objects.filter(pk=camera.pk).update(count=F('count')+1)
            
        else:
            logger.info("We've seen this camera (%s) for this user before, updating counts." % (camera))
            
            # Update counts
            FlickrUserCamera.objects.filter(pk=flickr_user_camera.pk).update(count_photos=F('count_photos')+1)
            
            if photo.comments_count:
                FlickrUserCamera.objects.filter(pk=flickr_user_camera.pk).update(comments_count=F('comments_count')+int(photo.comments_count))
                
            if photo.faves_count:
                FlickrUserCamera.objects.filter(pk=flickr_user_camera.pk).update(faves_count=F('faves_count')+int(photo.faves_count))
                
        return
        
    return
    
@task
def fetch_flickr_contacts(nsid):
    logger.info("Fetching contacts for Flickr user %s." % (nsid))
    
@task
def delete_flickr_user(nsid, reset=False):
    logger.info("Clearing cameras and photos for Flickr user %s." % (nsid))
    flickr_user = FlickrUser.objects.get(pk = nsid)
    user_cameras = flickr_user.flickrusercamera_set.all()
    
    for user_camera in user_cameras:
        logger.info("Updating camera %s to remove this user's photos from counts." % (user_camera.camera.name))
        Camera.objects.filter(pk=user_camera.camera.pk).update(count=F('count')-1)
        Camera.objects.filter(pk=user_camera.camera.pk).update(count_photos=F('count_photos')-int(user_camera.count_photos))
        
        logger.info("Removing Flickr user camera.")
        user_camera.delete()
        
    logger.info("Pulling and deleting photos for %s." % (nsid))
    photos = Photo.objects.filter(owner_nsid = flickr_user.nsid).all()
    photos.delete()
    
    if reset:
        flickr_user.count_photos_processed = None
        flickr_user.date_last_photo_update = None
        flickr_user.save()
    else:
        logger.info("Deleting Flickr user %s" % (nsid))
        flickr_user.delete()