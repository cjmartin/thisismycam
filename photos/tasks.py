from django.conf import settings

from django.utils import simplejson
from django.template.defaultfilters import slugify
from django.utils.hashcompat import md5_constructor as md5

from django.core.cache import cache
from django.db import IntegrityError
from django.db.models import F

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime

from celery.task import task
from celery import chord

from flickr_api.api import flickr
from flickr_api.base import FlickrError

import re
import time
import pytz
import urllib2
from urllib2 import URLError

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

@task()
def fetch_photos_for_flickr_user(results, nsid, page=1):
    nsid_digest = md5(nsid).hexdigest()
    lock_id = "%s-lock-%s" % ("fetch_photos", nsid_digest)
    
    ## When it's all working, re-enable this.
    # # cache.add fails if if the key already exists
    # acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    # 
    # if acquire_lock():
    
    flickr_user = FlickrUser.objects.get(nsid = nsid)
    
    per_page = 20
    
    logger.info("Fetching page %s for %s" % (page, flickr_user.username))
    
    try:
        # Fetch a page of photos
        photos_rsp = flickr.people.getPublicPhotos(
            user_id=flickr_user.nsid,
            per_page=per_page,
            page=page,
            extras="date_taken,date_upload,license,owner_name,media,path_alias,count_comments,count_faves,geo",
            format="json",
            nojsoncallback="true",
        )
        json = simplejson.loads(photos_rsp)
        
        if json and json['stat'] == 'ok':
            pages = json['photos']['pages']
            photo_updates = []
            
            for photo in json['photos']['photo']:
                photo_updates.append(process_flickr_photo.subtask((photo, flickr_user.nsid), link=update_flickr_user_camera.subtask((flickr_user.nsid, ))))
                
            if page == pages:
                logger.info("This is the last page (%s) for %s!" % (pages, flickr_user.username))
                return chord(photo_updates)(flickr_user_fetch_photos_complete.subtask((flickr_user.nsid, )))
                
            else:
                logger.info("Firing tasks for page %s of %s for %s" % (page, pages, flickr_user.username))
                next_page = page + 1
                return chord(photo_updates)(fetch_photos_for_flickr_user.subtask((flickr_user.nsid, next_page, )))
                
        else:
            logger.error("Flickr api query did not respond OK, will try again.")
            return fetch_photos_for_flickr_user.delay(None, user.nsid, page)
            
    except URLError:
        logger.error("Problem talking to Flickr (URLError), will try again.")
        return fetch_photos_for_flickr_user.delay(None, user.nsid, page)
        
    except FlickrError, e:
        logger.error("Problem talking to Flickr (FlickrError), re-scheduling task.\n Error: %s" % (e))
        raise fetch_photos_for_flickr_user.retry(countdown=1)
        
    ## When it's all working, re-enable this.
    # 
    # print "Photos for %s have already been fetched within the last hour." % (flickr_user.username)
    # return

@task()
def process_flickr_photo(api_photo, nsid):
    logger.info("Processing photo %s for user %s.\n" % (api_photo['id'], nsid))
    
    try:
        # Query Flickr for this photo's Exif data
        exif_rsp = flickr.photos.getExif(photo_id=api_photo['id'],format="json",nojsoncallback="true")
        exif = simplejson.loads(exif_rsp)
        
        # If it exists, process it
        if exif and exif['stat'] == 'ok':
            exif_camera = ""
            raw_exif_make = ""
            exif_make = ""
            raw_exif_model = ""
            exif_model = ""
            exif_software = ""
        
            for tag in exif['photo']['exif'] :
                if tag['label'] == "Make" :
                    raw_exif_make = tag['raw']['_content']
                                    
                if tag['label'] == "Model" :
                    raw_exif_model = tag['raw']['_content']
                                    
                if tag['label'] == "Software" :
                    exif_software = tag['raw']['_content']
                    
            # This is the "name" that Flickr uses, it's usually nice
            # if exif['photo']['camera']:
            #    exif_camera = exif['photo']['camera']
            
            # Create a clean version of the raw Exif make
            exif_make = clean_make(raw_exif_make)
            
            # Create a clean version of the raw Exif model, and remove the make if it's duplicated
            exif_model = clean_model(raw_exif_model, exif_make)
                
            # If there's a model (camera) we'll carry on
            if exif_model:
                
                # Process the date taken and date upload into nice time objecs
                
                # Date taken is a time string of the local time when the photo was taken,
                # we don't know the time zone, so we'll store it as UTC and always display it as UTC
                naive = parse_datetime(api_photo['datetaken'])
                api_date_taken = pytz.timezone("UTC").localize(naive)
                
                # Date upload is a unix timestamp, so we can store it as UTC and convert to whatever tz we want.
                api_date_upload = datetime.utcfromtimestamp(float(api_photo['dateupload'])).replace(tzinfo=timezone.utc)
                
                # Create the camera slug with things that should never change
                # I would use exif_camera, but I'm afraid those might change on Flickr's side
                camera_slug = slugify(exif_make + " " + exif_model)
                
                # Create a name for the camera
                if exif_make:
                    camera_name = exif_make + " " + exif_model
                else:
                    camera_name = exif_model
                        
                # Try to create the camera, or get it if it existsg
                try:
                    camera, created = Camera.objects.get_or_create(
                        slug = camera_slug,
                        defaults = {
                            'name': camera_name,
                            'model': exif_model,
                            'exif_model': raw_exif_model,
                            'exif_make': raw_exif_make,
                            'count': 1,
                        }
                    )
                    
                except IntegrityError:
                    logger.warning("Camera %s already exists, but we're trying to add it again. Rescheduling task." % (exif_camera))
                    raise process_flickr_photo.retry(countdown=1)
                    
                if created:
                    if exif_make:
                        make_slug = slugify(exif_make)
                        
                        try:
                            make, created = Make.objects.get_or_create(
                                slug = make_slug,
                                defaults = {
                                    'name': exif_make,
                                    'count': 1,
                                }
                            )
                            
                        except IntegrityError:
                            logger.warning("Make %s already exists, but we're trying to add it again. Rescheduling task." % (exif_make))
                            raise process_flickr_photo.retry(countdown=1)
                            
                        if not created:
                            Make.objects.filter(slug=make_slug).update(count=F('count')+1)
                            
                        camera.make = make
                        camera.save()
                
                # In case we need to create cache keys
                id_digest = md5(str(camera.id)).hexdigest()
                
                # A little bonus here, if the camera doesn't have aws info, try to get it.
                if not camera.amazon_item_response:
                    lock_id = "%s-lock-%s" % ("aws_update", id_digest)
                    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
                    
                    if acquire_lock():
                        logger.info("Fetching aws info for %s." % (camera.name))
                        add_aws_item_to_camera.delay(camera.id)
                        
                    else:
                        logger.info("AWS item update for %s already scheduled, skipping." % (camera.name))
                        
                else:
                    if not camera.amazon_image_response:
                        lock_id = "%s-lock-%s" % ("aws_image_update", id_digest)
                        acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
                        
                        if acquire_lock():
                            logger.info("%s already has aws info, but no photos, will fetch." % (camera.name))
                            add_aws_photos_to_camera.delay(camera.id)
                            
                        else:
                            logger.info("AWS image update for %s already scheculed, skipping." % (camera.name))
                            
                photo, created = Photo.objects.get_or_create(
                    photo_id = api_photo['id'],
                    defaults = {
                        'secret': api_photo['secret'],
                        'server': api_photo['server'],
                        'farm': api_photo['farm'],
                        'license': api_photo['license'],
                        'media': api_photo['media'],
                        'owner_nsid': api_photo['owner'],
                        'owner_name': api_photo['ownername'],
                        'date_taken': api_date_taken,
                        'date_upload': api_date_upload,
                        'camera': camera,
                    }
                )
                
                photo.title = api_photo['title']
                photo.path_alias = api_photo['pathalias']
                photo.date_taken = api_date_taken
                photo.date_upload = api_date_upload
                photo.comments_count = api_photo['count_comments']
                photo.faves_count = api_photo['count_faves']
                
                if camera.make:
                    photo.camera_make = camera.make
                    
                if api_photo['latitude'] or api_photo['longitude'] and api_photo['geo_is_public']:
                    photo.has_geo =  1
                    photo.latitude = api_photo['latitude']
                    photo.longitude = api_photo['longitude']
                    photo.accuracy = api_photo['accuracy']
                    photo.context = api_photo['context']
                    
                else:
                    photo.has_geo = 0
                    
                # Ok, save the photo.
                logger.info("Saving photo %s for camera %s.\n" % (photo.photo_id, camera.name))
                photo.save()
                
                if created:
                    Camera.objects.filter(slug=camera_slug).update(count=F('count')+1)
                    return photo.photo_id
                    
                else:
                    return False
                    
            # The photo doesn't have camera info
            else:
                return False
                
    except URLError:
        logger.error("Problem talking to Flickr (URLError), re-scheduling task.")
        raise fetch_photos_for_flickr_user.retry(countdown=1)
        
    except FlickrError, e:
        logger.error("Problem talking to Flickr (FlickrError), re-scheduling task.\n Error: %s" % (e))
        raise fetch_photos_for_flickr_user.retry(countdown=1)
                    
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
    'None',
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
    make = re.sub(r'(?i)(^htc_)', "HTC", make)
    make = re.sub(r'(?i)(^verizon_)', "Verizon", make)

    make = re.sub("[<>]", "", make)
    make = re.sub(" +", " ", make)
    make = make.strip('.-+<>{}[] ')

    if make == "KONICA" or make == "MINOLTA" or make == "Konica Minolta Photo Imaging":
        make = "Konica Minolta"

    if make == "LGE" or make == "lge" or make == "LG Electronics" or make == "lg" or make == "LG ELEC" or make == "LG_Electronics":
        make = "LG"

    if make == "made by Polaroid":
        make = "Polaroid"

    if make == "FUJI":
        make = "Fujifilm"
        
    # Special case for custom LG Android Rom
    if make == "InferiorHumanOrgans":
        make = "LG"
        
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
    model = model.strip('.-+<>{}[] ')

    # More Motorola
    if model == "DROIDX":
        model = "DROID X"

    if model == "DROID2":
        model = "DROID 2"
        
    # Special case for custom LG Android Rom
    if make == "LG":
        if model == "thunderc":
            model = "Optimus"
            
        if model == "thunderg" or model == "p500":
            model = "Optimus One"
            
        if model == "P350":
            model = "Optimus Me"
            
    return model