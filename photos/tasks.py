from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils import simplejson, timezone
from datetime import datetime, date, timedelta

from celery.task import task
from flickr_api.api import flickr

from cameras.models import Make
from cameras.models import Camera
from cameras.tasks import add_aws_item_to_camera
from cameras.tasks import add_aws_photos_to_camera

from photos.models import Photo

import re
import time

@task(ignore_result=True)
def fetch_photos_for_flickr_user(user):
    page = 1
    pages = 1
    photos_processed = 0
    update_time = time.time()
    
    while page <= pages:
        print "Fetching page %s for %s" % (page, user.username)
        photos_rsp = flickr.people.getPublicPhotos(user_id=user.nsid,extras="date_taken,date_upload,license,owner_name,media,path_alias",page=page,format="json",nojsoncallback="true")
        json = simplejson.loads(photos_rsp)
    
        if json and json['stat'] == 'ok':
            pages = json['photos']['pages']
            for photo in json['photos']['photo']:
                if int(photo['dateupload']) >= user.date_last_photo_update:
                    if settings.DEBUG:
                        print "Go %s, %s is after %s" % (photo['id'], photo['dateupload'], user.date_last_photo_update)
                        process_flickr_photo(photo, user)
                    else:
                        process_flickr_photo.delay(photo, user)
                        
                    photos_processed+=1
                else:
                    print "Setting last photo update to %s for %s" % (update_time, user.username)
                    user.date_last_photo_update = update_time
                    page = pages
                    break
        else:
            break
            
        page+=1
        
    if not user.date_last_photo_update:
        print "Setting last photo update to %s for %s" % (update_time, user.username)
        user.date_last_photo_update = update_time
        
    print "Processed %s photos for %s" % (photos_processed, user.username)
    if user.count_photos_processed:
        photos_processed = photos_processed + user.count_photos_processed
        
    user.count_photos_processed = photos_processed
    user.save()
    
    print "That was fun!"
    
@task(ignore_result=True)
def process_flickr_photo(api_photo, user):
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
                path_alias = api_photo['pathalias']
            )

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
                    'count_day' : day_count,
                }

                camera = Camera.objects.create(**args)

            photo.camera = camera

            print "Saving photo %s for camera %s.\n" % (photo.photo_id, camera.name)    
            photo.save()

            if not camera.amazon_item_response:
                if settings.DEBUG:
                    print "Fetching aws info for %s.\n" % camera.name
                    add_aws_item_to_camera(camera)
                else:
                    add_aws_item_to_camera.delay(camera)
            else:
                if not camera.amazon_image_response:
                    if settings.DEBUG:
                        print "%s already has aws info.\n" % camera.name
                        add_aws_photos_to_camera(camera)
                    else:
                        add_aws_photos_to_camera.delay(camera)
                        
            print "Ooh, there's a user (%s), lets update that they have this camera (%s)." % (user, camera.id)
            try:
                flickr_user_camera = FlickrUserCamera.objects.get(flickr_user=user, camera=camera)
                flickr_user_camera.count_photos = flickr_user_camera.count_photos + 1
                flickr_user_camera.save()
                print "We've already seen this camera for this user, updating the count."

            except FlickrUserCamera.DoesNotExist:
                print "We've never seen this camera for this user, lets add it."
                flickr_user_camera = FlickrUserCamera.objects.create(
                    camera = camera,
                    flickr_user = user,
                    count_photos = 1,
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