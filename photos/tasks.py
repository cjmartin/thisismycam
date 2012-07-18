from django.conf import settings

from django.utils import simplejson
from django.template.defaultfilters import slugify
from django.utils.hashcompat import md5_constructor as md5

from django.core.cache import cache
from django.db import IntegrityError

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime

from celery.task import task
from celery import chord

from flickr_api.api import flickr

import re
import time
import pytz
import urllib2

from cameras.models import Make
from cameras.models import Camera
from cameras.tasks import add_aws_item_to_camera
from cameras.tasks import add_aws_photos_to_camera

from flickr.models import FlickrUser
from flickr.tasks import update_flickr_user_camera
from flickr.tasks import flickr_user_fetch_photos_complete

from photos.models import Photo

import logging
logger = logging.getLogger(__name__)

LOCK_EXPIRE = 60 * 60 # Lock expires in 60 minutes

@task(ignore_result=True)
def fetch_photos_for_flickr_user(nsid):
    flickr_user = FlickrUser.objects.get(nsid = nsid)
    
    nsid_digest = md5(flickr_user.nsid).hexdigest()
    lock_id = "%s-lock-%s" % ("fetch_photos", nsid_digest)
    
    # # cache.add fails if if the key already exists
    # acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    # 
    # if acquire_lock():
    page = 1
    pages = 1
    photos_processed = 0
    update_time = time.time()
    
    photo_updates = []
    
    while page <= pages:
        logger.info("Fetching page %s for %s" % (page, flickr_user.username))
        try:
            photos_rsp = flickr.people.getPublicPhotos(user_id=flickr_user.nsid,extras="date_taken,date_upload,license,owner_name,media,path_alias,count_comments,count_faves,geo",page=page,format="json",nojsoncallback="true")
            json = simplejson.loads(photos_rsp)

            if json and json['stat'] == 'ok':
                pages = json['photos']['pages']
                
                for photo in json['photos']['photo']:
                    if int(photo['dateupload']) >= flickr_user.date_last_photo_update:
                        logger.info("Adding photo %s to task group, %s is after %s" % (photo['id'], photo['dateupload'], flickr_user.date_last_photo_update))
                        
                        photo_updates.append(process_flickr_photo.subtask((photo, flickr_user.nsid)))
                        photos_processed+=1
                        
                    else:
                        page = pages
                        break
                        
            else:
                logger.error("Flickr api query did not respond OK, re-scheduling task.")
                raise fetch_photos_for_flickr_user.retry()
        
            # page+=1
            page = pages+1
            
        except urllib2.URLError as e:
            logger.error("Problem talking to Flickr due to %s, re-scheduling task." % (e.reason))
            raise fetch_photos_for_flickr_user.retry()
            
    logger.info("Tuna blaster engaged, FIRING!")
    chord(photo_updates)(flickr_user_fetch_photos_complete.subtask((nsid, photos_processed, update_time)))
    # 
    # print "Photos for %s have already been fetched within the last hour." % (flickr_user.username)
    # return
    
@task(ignore_result=True)
def process_flickr_photo(api_photo, nsid):
    loger.info("Processing photo %s for user %s.\n" % (api_photo['id'], nsid))
    return
    # try:
    #     exif_rsp = flickr.photos.getExif(photo_id=api_photo['id'],format="json",nojsoncallback="true")
    #     exif = simplejson.loads(exif_rsp)
    # 
    #     if exif and exif['stat'] == 'ok':
    #         exif_camera = ""
    #         raw_exif_make = ""
    #         exif_make = ""
    #         raw_exif_model = ""
    #         exif_model = ""
    #         exif_software = ""
    #     
    #         for tag in exif['photo']['exif'] :
    #             if tag['label'] == "Make" :
    #                 raw_exif_make = tag['raw']['_content']
    #                 exif_make = clean_make(tag['raw']['_content'])
    #             
    #             if tag['label'] == "Model" :
    #                 raw_exif_model = tag['raw']['_content']
    #                 exif_model = clean_model(tag['raw']['_content'], exif_make)
    #             
    #             if tag['label'] == "Software" :
    #                 exif_software = tag['raw']['_content']
    #             
    #         if exif['photo']['camera']:
    #             exif_camera = exif['photo']['camera']
    #         
    #         if exif_model:
    #             naive = parse_datetime(api_photo['datetaken'])
    #             api_date_taken = pytz.timezone("UTC").localize(naive)
    #         
    #             api_date_upload = datetime.utcfromtimestamp(float(api_photo['dateupload'])).replace(tzinfo=timezone.utc)
    #         
    #             photo = Photo(
    #                 photo_id = api_photo['id'],
    #                 secret = api_photo['secret'],
    #                 server = api_photo['server'],
    #                 farm = api_photo['farm'],
    #                 title = api_photo['title'],
    #                 license = api_photo['license'],
    #                 media = api_photo['media'],
    #                 owner_nsid = api_photo['owner'],
    #                 owner_name = api_photo['ownername'],
    #                 path_alias = api_photo['pathalias'],
    #                 date_taken = api_date_taken,
    #                 date_upload = api_date_upload,
    #                 comments_count = api_photo['count_comments'],
    #                 faves_count = api_photo['count_faves'],
    #             )
    #         
    #             if api_photo['latitude'] or api_photo['longitude'] and api_photo['geo_is_public']:
    #                 photo.has_geo =  1
    #                 photo.latitude = api_photo['latitude']
    #                 photo.longitude = api_photo['longitude']
    #                 photo.accuracy = api_photo['accuracy']
    #                 photo.context = api_photo['context']
    #             
    #                 # try:
    #                 #     flickr_place = FlickrPlace.objects.get(place_id = api_photo['place_id'])
    #                 # except FlickrPlace.DoesNotExist:
    #                 #     flickr_place = FlickrPlace(
    #                 #         place_id = api_photo['place_id'],
    #                 #     )
    #                 #     flickr_place.save()
    #                 #     
    #                 #     if settings.DEBUG:
    #                 #         print "Fetching data for Flickr place %s" % flickr_place.place_id
    #                 #         process_flickr_place(flickr_place.place_id)
    #                 #     else:
    #                 #         process_flickr_place.delay(flickr_place.place_id)
    #                 #     
    #                 # photo.flickr_place = flickr_place
    #             else:
    #                 photo.has_geo = 0
    #             
    #             camera_slug = slugify(exif_make + " " + exif_model)
    #         
    #             try:
    #                 camera = Camera.objects.get(slug = camera_slug)
    #                 photo.camera_make = camera.make
    #             
    #             except Camera.DoesNotExist:
    #                 make = None
    #                 if exif_make:
    #                     make_slug = slugify(exif_make)
    #                     try:
    #                         make = Make.objects.get(slug = make_slug)
    #                         make.count = make.count + 1
    #                     
    #                     except Make.DoesNotExist:
    #                         make = Make(
    #                             slug = make_slug,
    #                             name = exif_make,
    #                             count = 1
    #                         )
    #                     
    #                     try:
    #                         make.save()
    #                     except IntegrityError:
    #                         raise process_flickr_photo.retry()
    #                     
    #                 photo.camera_make = make
    #             
    #                 if not exif_camera:
    #                     if exif_make:
    #                         exif_camera = exif_make + " " + exif_model
    #                     else:
    #                         exif_camera = exif_model
    #                     
    #                 args = {
    #                     'slug' : camera_slug,
    #                     'name' : exif_camera,
    #                     'make' : make,
    #                     'exif_make' : raw_exif_make,
    #                     'model' : exif_model,
    #                     'exif_model' : raw_exif_model,
    #                     'count' : 0,
    #                 }
    #             
    #                 try:
    #                     camera = Camera.objects.create(**args)
    #                 except IntegrityError:
    #                     raise process_flickr_photo.retry()
    #                 
    #             photo.camera = camera
    #         
    #             print "Saving photo %s for camera %s.\n" % (photo.photo_id, camera.name)    
    #             photo.save()
    #         
    #             # In case we need to create cache keys
    #             id_digest = md5(str(camera.id)).hexdigest()
    #         
    #             if not camera.amazon_item_response:
    #                 lock_id = "%s-lock-%s" % ("aws_update", id_digest)
    #                 acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    #             
    #                 if acquire_lock():
    #                     if settings.DEBUG:
    #                         print "Fetching aws info for %s.\n" % camera.name
    #                         add_aws_item_to_camera(camera.id)
    #                     else:
    #                         add_aws_item_to_camera.delay(camera.id)
    #                 else:
    #                     print "AWS item update for %s already scheculed, skipping." % (camera.name)
    #                 
    #             else:
    #                 if not camera.amazon_image_response:
    #                     lock_id = "%s-lock-%s" % ("aws_image_update", id_digest)
    #                     acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    #                 
    #                     if acquire_lock():
    #                         if settings.DEBUG:
    #                             print "%s already has aws info.\n" % camera.name
    #                             add_aws_photos_to_camera(camera.id)
    #                         else:
    #                             add_aws_photos_to_camera.delay(camera.id)
    #                     else:
    #                         print "AWS image update for %s already scheculed, skipping." % (camera.name)
    #         
    #             # Update the FlickrUserCamera
    #             if settings.DEBUG:
    #                 update_flickr_user_camera(nsid, camera.id, photo.photo_id)
    #             else:
    #                 update_flickr_user_camera.delay(nsid, camera.id, photo.photo_id)
    #                 
    # except urllib2.URLError as e:
    #     print "Problem talking to Flickr due to %s, re-scheduling task." % (e.reason)
    #     raise fetch_photos_for_flickr_user.retry()
                    
def clean_make(make):
    crap_words = [
    'PHOTO FILM CO\., LTD\.',
    'COMPUTER CO\.,LTD\.',
    'COMPUTER CO\.,LTD',
    'Optical Co\.,Ltd\.',
    'Optical Co\.,Ltd',
    'OPTICAL CO\.,LTD\.',
    'OPTICAL CO\.,LTD',
    'OPTICAL CO,\.LTD\.',
    'TECHWIN CO\., LTD\.',
    'TECHWIN CO\., LTD',
    'TECHWIN Co\.',
    'IMAGING CORP\.',
    '_IMAGING_CORP\.',
    'Camera AG',
    'Camera, Inc\.',
    'Electric Co\. Ltd\.',
    'Electric Co\.,Ltd\.',
    'Electric Co\.,Ltd',
    'Electric Co\., Ltd\.',
    'Electric Co\., Ltd',
    'Europe Ltd\. in\.',
    'Co\., Ltd\.',
    'Co\., Ltd',
    'Co\.,Ltd\.',
    'Co\.,Ltd',
    '\(C\) 2003',
    ', Inc\.',
    ', Inc',
    ',Inc\.',
    ',Inc',
    'Inc\.',
    'Inc',
    'CORPORATION',
    'COMPANY',
    'CORP\.',
    'CORP',
    'TECHWIN',
    'GmbH',
    'ELEC\.',
    ]

    for word in crap_words:
        make = re.sub(r'(?i)(' + word + ')', "", make)

    make = re.sub(r'(?i)(SEIKO EPSON)', "EPSON", make)
    make = re.sub(r'(?i)(EASTMAN KODAK)', "Kodak", make)
    make = re.sub(r'(?i)(SAMSUNG ELECTRONICS)', "Samsung", make)
    make = re.sub(r'(?i)(SAMSUNG DIGITAL IMA)', "Samsung", make)
    make = re.sub(r'(?i)(tmobile)', "T-Mobile", make)
    make = re.sub(r'(?i)(^Motorola.+)', "Motorola", make)
    make = re.sub(r'(?i)(virgin_mobile)', "Virgin Mobile", make)

    make = re.sub("[<>]", "", make)
    make = re.sub(" +", " ", make)
    make = make.strip()

    if make == "KONICA" or make == "MINOLTA" or make == "Konica Minolta Photo Imaging":
        make = "Konica Minolta"

    if make == "LGE" or make == "lge" or make == "LG" or make == "lg" or make == "LG ELEC" or make == "LG_Electronics":
        make = "LG Electronics"

    if make == "htc_asia_india" or make == "htc_asia_tw" or make == "htc_wwe" or make == "htc_asia_wwe" or make == "htc_europe":
        make = "HTC"

    if make == "verizon_wwe":
        make = "Verizon"

    if make == "made by Polaroid":
        make = "Polaroid"

    if make == "FUJI":
        make = "Fujifilm"

    return make

def clean_model(model, make):
    crap_words = [
    'DIGITAL CAMERA',
    ]

    # Remove crappy words
    for word in crap_words:
        model = re.sub(r'(?i)(' + word + ')', "", model)

    # Specific cases to handle before removing the make
    if model == "LEICA CAMERA AG LEICA X1": # Sometimes we have an X1 without a make
        model = "LEICA X1" # This will make the slug match the good ones

    # Camera ZOOM FX
    model = re.sub(r"(?i)(^Camera ZOOM FX for Android.+)", "Camera Zoom FX for Android", model)

    # Remove the make if it's in the model
    model = re.sub(r'(?i)(' + make + ')', "", model)

    # A whole section just for fixing Motorola bullshit
    model = re.sub(r"(?i)(^DROIDX\s[0-9][0-9a-z]+)", "DROID X", model)
    model = re.sub(r"(?i)(^DROID2\s[0-9][0-9a-z]+)", "DROID 2", model)
    model = re.sub(r"(?i)(^MB525\s[0-9][0-9a-z]+)", "MB525", model)

    # Strip some nasty characters, and extra spaces
    model = re.sub("[<>]", "", model)
    model = re.sub(" +", " ", model)
    model = model.strip()

    # More Motorola
    if model == "DROIDX":
        model = "DROID X"

    if model == "DROID2":
        model = "DROID 2"

    return model