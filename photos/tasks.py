from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils import simplejson, timezone
from django.utils.dateparse import parse_datetime
from django.core.cache import cache

from datetime import datetime, date, timedelta

from celery.task import task
from flickr_api.api import flickr

from cameras.models import Make
from cameras.models import Camera
from cameras.tasks import add_aws_item_to_camera
from cameras.tasks import add_aws_photos_to_camera

from flickr.models import FlickrUser
from flickr.models import FlickrUserCamera
# from flickr.models import FlickrPlace
# from flickr.tasks import process_flickr_place

from photos.models import Photo

import re
import time
import pytz

LOCK_EXPIRE = 60 * 60 # Lock expires in 60 minutes

@task(ignore_result=True)
def fetch_photos_for_flickr_user(nsid):
    flickr_user = FlickrUser.objects.get(nsid = nsid)
    
    # The cache key consists of the task name and the MD5 digest
    # of the feed URL.
    nsid_digest = md5(flickr_user.nsid).hexdigest()
    lock_id = "%s-lock-%s" % (self.name, nsid_digest)
    
    # cache.add fails if if the key already exists
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    
    if acquire_lock():
        page = 1
        pages = 1
        photos_processed = 0
        update_time = time.time()
    
        while page <= pages:
            print "Fetching page %s for %s" % (page, flickr_user.username)
            photos_rsp = flickr.people.getPublicPhotos(user_id=flickr_user.nsid,extras="date_taken,date_upload,license,owner_name,media,path_alias,count_comments,count_faves,geo",page=page,format="json",nojsoncallback="true")
            json = simplejson.loads(photos_rsp)
    
            if json and json['stat'] == 'ok':
                pages = json['photos']['pages']
                for photo in json['photos']['photo']:
                    if int(photo['dateupload']) >= flickr_user.date_last_photo_update:
                        if settings.DEBUG:
                            print "Go %s, %s is after %s" % (photo['id'], photo['dateupload'], flickr_user.date_last_photo_update)
                            process_flickr_photo(photo, flickr_user.nsid)
                        else:
                            process_flickr_photo.delay(photo, flickr_user.nsid)
                        
                        photos_processed+=1
                    else:
                        print "Setting last photo update to %s for %s" % (update_time, flickr_user.username)
                        flickr_user.date_last_photo_update = update_time
                        page = pages
                        break
            else:
                break
            
            page+=1
        
        if not flickr_user.date_last_photo_update:
            print "Setting last photo update to %s for %s" % (update_time, flickr_user.username)
            flickr_user.date_last_photo_update = update_time
        
        print "Processed %s photos for %s" % (photos_processed, flickr_user.username)
        if flickr_user.count_photos_processed:
            photos_processed = photos_processed + flickr_user.count_photos_processed
        
        flickr_user.count_photos_processed = photos_processed
        flickr_user.save()
        
        print "That was fun!"
        return
    
    print "Photos for %s have already been fetched within the last hour." % (flickr_user.username)
    return
    
@task(ignore_result=True)
def process_flickr_photo(api_photo, nsid):
    exif_rsp = flickr.photos.getExif(photo_id=api_photo['id'],format="json",nojsoncallback="true")
    exif = simplejson.loads(exif_rsp)

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
                exif_make = clean_make(tag['raw']['_content'])

            if tag['label'] == "Model" :
                raw_exif_model = tag['raw']['_content']
                exif_model = clean_model(tag['raw']['_content'], exif_make)

            if tag['label'] == "Software" :
                exif_software = tag['raw']['_content']

        if exif['photo']['camera']:
            exif_camera = exif['photo']['camera']

        if exif_model:
            naive = parse_datetime(api_photo['datetaken'])
            api_date_taken = pytz.timezone("UTC").localize(naive)
            
            api_date_upload = datetime.utcfromtimestamp(float(api_photo['dateupload'])).replace(tzinfo=timezone.utc)
            
            photo = Photo(
                photo_id = api_photo['id'],
                secret = api_photo['secret'],
                server = api_photo['server'],
                farm = api_photo['farm'],
                title = api_photo['title'],
                license = api_photo['license'],
                media = api_photo['media'],
                owner_nsid = api_photo['owner'],
                owner_name = api_photo['ownername'],
                path_alias = api_photo['pathalias'],
                date_taken = api_date_taken,
                date_upload = api_date_upload,
                comments_count = api_photo['count_comments'],
                faves_count = api_photo['count_faves'],
            )
            
            if api_photo['latitude'] or api_photo['longitude'] and api_photo['geo_is_public']:
                photo.has_geo =  1
                photo.latitude = api_photo['latitude']
                photo.longitude = api_photo['longitude']
                photo.accuracy = api_photo['accuracy']
                photo.context = api_photo['context']
                
                # try:
                #     flickr_place = FlickrPlace.objects.get(place_id = api_photo['place_id'])
                # except FlickrPlace.DoesNotExist:
                #     flickr_place = FlickrPlace(
                #         place_id = api_photo['place_id'],
                #     )
                #     flickr_place.save()
                #     
                #     if settings.DEBUG:
                #         print "Fetching data for Flickr place %s" % flickr_place.place_id
                #         process_flickr_place(flickr_place.place_id)
                #     else:
                #         process_flickr_place.delay(flickr_place.place_id)
                #     
                # photo.flickr_place = flickr_place
            else:
                photo.has_geo = 0

            camera_slug = slugify(exif_make + " " + exif_model)

            try:
                camera = Camera.objects.get(slug = camera_slug)
                photo.camera_make = camera.make

            except Camera.DoesNotExist:
                make = None
                if exif_make:
                    make_slug = slugify(exif_make)
                    try:
                        make = Make.objects.get(slug = make_slug)
                        make.count = make.count + 1

                    except Make.DoesNotExist:
                        make = Make(
                            slug = make_slug,
                            name = exif_make,
                            count = 1
                        )

                    make.save()
                    photo.camera_make = make

                if not exif_camera:
                    if exif_make:
                        exif_camera = exif_make + " " + exif_model
                    else:
                        exif_camera = exif_model

                args = {
                    'slug' : camera_slug,
                    'name' : exif_camera,
                    'make' : make,
                    'exif_make' : raw_exif_make,
                    'model' : exif_model,
                    'exif_model' : raw_exif_model,
                    'count' : 0,
                }

                camera = Camera.objects.create(**args)

            photo.camera = camera

            print "Saving photo %s for camera %s.\n" % (photo.photo_id, camera.name)    
            photo.save()

            if not camera.amazon_item_response:
                lock_id = "%s-lock-%s" % ("aws_update", camera.id)
                acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
                
                if acquire_lock():
                    if settings.DEBUG:
                        print "Fetching aws info for %s.\n" % camera.name
                        add_aws_item_to_camera(camera.id)
                    else:
                        add_aws_item_to_camera.delay(camera.id)
                else:
                    print "AWS item update for %s already scheculed, skipping." % (camera.name)
                    
            else:
                if not camera.amazon_image_response:
                    lock_id = "%s-lock-%s" % ("aws_image_update", camera.id)
                    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
                    
                    if acquire_lock():
                        if settings.DEBUG:
                            print "%s already has aws info.\n" % camera.name
                            add_aws_photos_to_camera(camera.id)
                        else:
                            add_aws_photos_to_camera.delay(camera.id)
                    else:
                        print "AWS image update for %s already scheculed, skipping." % (camera.name)
            
            flickr_user = FlickrUser.objects.get(nsid = nsid)
            print "Ooh, there's a flickr_user (%s), lets update that they have this camera (%s)." % (flickr_user, camera.id)
            try:
                flickr_user_camera = FlickrUserCamera.objects.get(flickr_user=flickr_user, camera=camera)
                flickr_user_camera.count_photos = flickr_user_camera.count_photos + 1
                
                if photo.date_taken > flickr_user_camera.date_last_taken:
                    flickr_user_camera.date_last_taken = photo.date_taken
                    flickr_user_camera.last_taken_id = photo.photo_id
                elif photo.date_taken < flickr_user_camera.date_first_taken:
                    flickr_user_camera.date_first_taken = photo.date_taken
                    flickr_user_camera.first_taken_id = photo.photo_id
                    
                if photo.date_upload > flickr_user_camera.date_last_upload:
                    flickr_user_camera.date_last_upload = photo.date_upload
                    flickr_user_camera.last_upload_id = photo.photo_id
                elif photo.date_upload < flickr_user_camera.date_first_upload:
                    flickr_user_camera.date_first_upload = photo.date_upload
                    flickr_user_camera.first_upload_id = photo.photo_id
                    
                flickr_user_camera.comments_count = flickr_user_camera.comments_count + int(photo.comments_count)
                flickr_user_camera.faves_count = flickr_user_camera.faves_count + int(photo.faves_count)
                
                flickr_user_camera.save()
                print "We've already seen this camera for this user, updating the count."

            except FlickrUserCamera.DoesNotExist:
                print "We've never seen this camera for this user, lets add it."
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
    model = re.sub(r'(?i)(^' + make + ')', "", model)

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