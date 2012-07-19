from django.conf import settings
from django.utils import simplejson
from django.db import IntegrityError
from django.db import transaction

from celery.task import task
from flickr_api.api import flickr

from flickr.models import FlickrUser
from flickr.models import FlickrUserCamera
#from flickr.models import FlickrPlace

from cameras.models import Camera

from photos.models import Photo

import logging
logger = logging.getLogger(__name__)

@task()
def flickr_user_fetch_photos_complete(results):
    # flickr_user = FlickrUser.objects.get(nsid = nsid)
    # 
    # if last_page:
    #     logger.info("Setting last photo update to %s for %s" % (update_time, flickr_user.username))
    #     flickr_user.date_last_photo_update = update_time
    # 
    # logger.info("Processed %s photos for %s" % (len(photos_processed), flickr_user.username))
    # if flickr_user.count_photos_processed:
    #     photos_processed = len(photos_processed) + flickr_user.count_photos_processed
    # 
    # flickr_user.count_photos_processed = photos_processed
    # flickr_user.save()
    
    # logger.info("Fetch for %s complete. That was fun!" % (flickr_user.username))
    logger.info("Fetch complete. That was fun!")
    return

@task()
def update_flickr_user_camera(photo_id, nsid):
    if photo_id:
        flickr_user = FlickrUser.objects.get(pk = nsid)
        photo = Photo.objects.get(pk = photo_id)
        camera = photo.camera
    
        print "Updating flickr_user (%s) with camera (%s)." % (flickr_user, camera)
        try:
            flickr_user_camera = FlickrUserCamera.objects.get(flickr_user=flickr_user, camera=camera)
            return
            # with transaction.commit_on_success():
            #     flickr_user_camera = FlickrUserCamera.objects.select_for_update().get(flickr_user=flickr_user, camera=camera)
            #     
            #     if photo.date_taken > flickr_user_camera.date_last_taken:
            #         flickr_user_camera.date_last_taken = photo.date_taken
            #         flickr_user_camera.last_taken_id = photo.photo_id
            #     elif photo.date_taken < flickr_user_camera.date_first_taken:
            #         flickr_user_camera.date_first_taken = photo.date_taken
            #         flickr_user_camera.first_taken_id = photo.photo_id
            #         
            #     if photo.date_upload > flickr_user_camera.date_last_upload:
            #         flickr_user_camera.date_last_upload = photo.date_upload
            #         flickr_user_camera.last_upload_id = photo.photo_id
            #     elif photo.date_upload < flickr_user_camera.date_first_upload:
            #         flickr_user_camera.date_first_upload = photo.date_upload
            #         flickr_user_camera.first_upload_id = photo.photo_id
            #         
            #     flickr_user_camera.count_photos = flickr_user_camera.count_photos + 1
            #     flickr_user_camera.comments_count = flickr_user_camera.comments_count + int(photo.comments_count)
            #     flickr_user_camera.faves_count = flickr_user_camera.faves_count + int(photo.faves_count)
            #         
            #     flickr_user_camera.save()
            #     logger.info("We've already seen this camera (%s) for this user, updating the count." % (camera))
            #     return

        except FlickrUserCamera.DoesNotExist:
            try:
                flickr_user_camera = FlickrUserCamera.objects.create(
                    camera = camera,
                    flickr_user = flickr_user,
                    count_photos = 1,
                    date_first_taken = photo.date_taken,
                    date_last_taken = photo.date_taken,
                    date_first_upload = photo.date_upload,
                    date_last_upload = photo.date_upload,
                    first_taken_id = photo.photo_id,
                    last_taken_id = photo.photo_id,
                    first_upload_id = photo.photo_id,
                    last_upload_id = photo.photo_id,
                    comments_count = photo.comments_count,
                    faves_count = photo.faves_count,
                )
                camera.count = camera.count + 1
                camera.save()
                logger.info("We've never seen this camera (%s) for this user, lets add it." % (camera))
                return
            
            except IntegrityError:
                logger.warning("FlickrUserCamera %s + %s already exists, but we're trying to add it again. Rescheduling task." % (flickr_user, camera))
                raise update_flickr_user_camera.retry()
                
    return
    
# @task(ignore_result=True)
# def process_flickr_place(flickr_place_id):
#     print "Fetching Flickr place for place id %s" % flickr_place_id
#     place_rsp = flickr.places.resolvePlaceId(place_id=flickr_place_id,format="json",nojsoncallback="true")
#     json = simplejson.loads(place_rsp)
# 
#     if json and json['stat'] == 'ok':
#         flickr_place = FlickrPlace.objects.get(place_id = flickr_place_id)
#         
#         location = json['location']
#         
#         flickr_place.woeid = location['woeid']
#         flickr_place.latitude = location['latitude']
#         flickr_place.longitude = location['longitude']
#         flickr_place.place_url = location['place_url']
#         flickr_place.place_type = location['place_type']
#         flickr_place.place_type_id = location['place_type_id']
#         
#         try:
#             if location['name']:
#                 flickr_place.name = location['name']
#         except:
#             True
#                     
#         try:
#             if location['timezone']:
#                 flickr_place.timezone = location['timezone']
#         except:
#             True
#         
#         try:
#             if location['neighbourhood']:
#                 flickr_place.neighbourhood_place_id = location['neighbourhood']['place_id']
#                 flickr_place.neighbourhood_woeid = location['neighbourhood']['woeid']
#                 flickr_place.neighbourhood_latitude = location['neighbourhood']['latitude']
#                 flickr_place.neighbourhood_longitude = location['neighbourhood']['longitude']
#                 flickr_place.neighbourhood_place_url = location['neighbourhood']['place_url']
#                 flickr_place.neighbourhood_name = location['neighbourhood']['_content']
#         except:
#             True
#         
#         try:
#             if location['locality']:
#                 flickr_place.locality_place_id = location['locality']['place_id']
#                 flickr_place.locality_woeid = location['locality']['woeid']
#                 flickr_place.locality_latitude = location['locality']['latitude']
#                 flickr_place.locality_longitude = location['locality']['longitude']
#                 flickr_place.locality_place_url = location['locality']['place_url']
#                 flickr_place.locality_name = location['locality']['_content']
#         except:
#             True
#             
#         try:
#             if location['county']:
#                 flickr_place.county_place_id = location['county']['place_id']
#                 flickr_place.county_woeid = location['county']['woeid']
#                 flickr_place.county_latitude = location['county']['latitude']
#                 flickr_place.county_longitude = location['county']['longitude']
#                 flickr_place.county_place_url = location['county']['place_url']
#                 flickr_place.county_name = location['county']['_content']
#         except:
#             True
#             
#         try:
#             if location['region']:
#                 flickr_place.region_place_id = location['region']['place_id']
#                 flickr_place.region_woeid = location['region']['woeid']
#                 flickr_place.region_latitude = location['region']['latitude']
#                 flickr_place.region_longitude = location['region']['longitude']
#                 flickr_place.region_place_url = location['region']['place_url']
#                 flickr_place.region_name = location['region']['_content']
#         except:
#             True
#         
#         try:
#             if location['country']:
#                 flickr_place.country_place_id = location['country']['place_id']
#                 flickr_place.country_woeid = location['country']['woeid']
#                 flickr_place.country_latitude = location['country']['latitude']
#                 flickr_place.country_longitude = location['country']['longitude']
#                 flickr_place.country_place_url = location['country']['place_url']
#                 flickr_place.country_name = location['country']['_content']
#         except:
#             True
#         
#         flickr_place.save()