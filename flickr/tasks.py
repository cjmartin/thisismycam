from django.conf import settings
from django.utils import simplejson
from django.db import IntegrityError
from django.utils.hashcompat import md5_constructor as md5
from django.core.cache import cache

from django.db.models import F
from django.db.models import Sum

import calendar
from datetime import datetime
from django.utils import timezone

import urllib
import urllib2
from urllib2 import URLError

from celery.task import task
from celery import chord

import flickr_api
from flickr_api.api import flickr
from flickr_api.base import FlickrError

from accounts.models import UserProfile

from flickr.models import FlickrUser
from flickr.models import FlickrUserCamera
from flickr.models import FlickrUserContact
from flickr.models import FlickrContactLookup

from cameras.models import Camera

from photos.models import Photo
from photos.tasks import process_flickr_photo

import logging
logger = logging.getLogger(__name__)

LOCK_EXPIRE = 60 * 60 # Lock expires in 60 minutes

@task()
def update_flickr_users(results, page=1, per_page=1, all_photos=False):
    limit = page * per_page
    offset = limit - per_page
    
    flickr_users = FlickrUser.objects.order_by('date_create')[offset:limit]
    user_updates = []
    
    for flickr_user in flickr_users:
        nsid_digest = md5(flickr_user.nsid).hexdigest()
        lock_id = "%s-lock-%s" % ("update_photos", nsid_digest)

        # cache.add fails if if the key already exists
        acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
        
        if acquire_lock:
            try:
                # First, update the flickr_user
                rsp = flickr.people.getInfo(user_id=flickr_user.nsid,format="json",nojsoncallback="true")
                json = simplejson.loads(rsp)
            
                if json and json['stat'] == "ok":
                    api_user = json['person']
                
                    flickr_user.username = api_user['username']['_content']
                    flickr_user.iconserver = api_user['iconserver']
                    flickr_user.iconfarm = api_user['iconfarm']
                    flickr_user.count_photos = api_user['photos']['count']['_content']

                    try:
                        flickr_user.realname = api_user['realname']['_content']
                    except KeyError:
                        flickr_user.realname = None

                    try:
                        flickr_user.path_alias = api_user['path_alias']
                    except KeyError:
                        flickr_user.path_alias = None

                    flickr_user.save()
            
            except URLError, e:
                logger.error("Problem talking to Flickr when calling people.getInfo from update_flickr_users (URLError), will try again. Reason: %s" % (e.reason))
                return update_photos_for_flickr_user.retry(countdown=5)
        
            except FlickrError, e:
                logger.error("Problem talking to Flickr when calling people.getInfo from update_flickr_users (FlickrError), re-scheduling task.\n Error: %s" % (e))
                raise update_photos_for_flickr_user.retry(countdown=5)
        
            user_updates.append(update_photos_for_flickr_user.subtask((None, flickr_user.nsid, None, all_photos)))
            
    if user_updates:
        next_page = page + 1
        return chord(user_updates)(update_flickr_users.subtask((next_page, per_page, all_photos, )))
        
@task()
def update_photos_for_flickr_user(results, nsid, page=None, update_all=False):
    flickr_user = FlickrUser.objects.get(pk=nsid)
    datetime_last_update = datetime.utcfromtimestamp(float(flickr_user.date_last_photo_update)).replace(tzinfo=timezone.utc)
    
    # If the user doesn't have any public photos, or they don't have any previously processed photos (probably exif off), skip.
    # Need a way to re-check the exif-off people, but re-scanning all their photos every time is too much.
    if flickr_user.count_photos == 0 or flickr_user.count_photos_processed == 0:
        return flickr_user_fetch_photos_complete.delay(None, flickr_user.nsid)

    if not page:
        page = 1

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
                logger.info("Checking photo for %s, this photo: %s | date update: %s" % (flickr_user.username, photo['dateupload'], flickr_user.date_last_photo_update))
                if update_all or int(photo['dateupload']) > int(flickr_user.date_last_photo_update):
                    logger.info("This photo is new!")
                    photo_updates.append(process_flickr_photo.subtask((photo, flickr_user.nsid), link=update_flickr_user_camera.subtask((flickr_user.nsid, ))))

            if photo_updates:
                logger.info("Firing update tasks for page %s of %s for %s" % (page, pages, flickr_user.username))

                if page == pages:
                    return chord(photo_updates)(flickr_user_fetch_photos_complete.subtask((flickr_user.nsid, datetime_last_update, )))

                else:
                    next_page = page + 1

                    pct = ((float(page) / float(pages)) * 100)
                    logger.info("pct should be: %s/%s * 100 = %s" % (page, pages, pct))

                    logger.info("Push it.")
                    values = {
                        'secret': settings.PUSHY_SECRET,
                        'user_id': flickr_user.nsid,
                        'message': simplejson.dumps({'type': 'fetch_photos.update_progress_bar', 'data': {'pct': pct}}),
                    }
                    data = urllib.urlencode(values)
                    req = urllib2.Request(settings.PUSHY_URL_LOCAL, data)

                    try:
                        response = urllib2.urlopen(req)
                    except:
                        logger.error("Problem calling pushy from photos update.")

                    logger.info("Scheduling chord of photo updates with callpack for next page")
                    return chord(photo_updates)(update_photos_for_flickr_user.subtask((flickr_user.nsid, next_page, update_all, )))

            else:
                logger.info("No more new photos, calling fetch photos complete")
                return flickr_user_fetch_photos_complete.delay(None, flickr_user.nsid, datetime_last_update)

        else:
            logger.error("Flickr api query did not respond OK calling getPublicPhotos for %s in update_photos, will try again." % (flickr_user.nsid))
            return update_photos_for_flickr_user.retry(countdown=5)

    except URLError, e:
        logger.error("Problem talking to Flickr when calling getPublicPhotos for %s in update_photos (URLError), will try again. Reason: %s" % (flickr_user.nsid, e.reason))
        return update_photos_for_flickr_user.retry(countdown=5)

    except FlickrError, e:
        logger.error("Problem talking to Flickr when calling getPublicPhotos for %s in update_photos (FlickrError), re-scheduling task.\n Error: %s" % (flickr_user.nsid, e))
        raise update_photos_for_flickr_user.retry(countdown=5)

    
@task()
def flickr_user_fetch_photos_complete(results, nsid, datetime_last_update=None):
    flickr_user = FlickrUser.objects.get(pk = nsid)
    
    fetch_cameras = True
    total_photos = 0
    
    try:
        last_upload = Photo.objects.filter(owner_nsid=flickr_user.nsid).latest('date_upload')
        logger.info("Awesome, %s user has photos!" % (flickr_user.username))
        
        logger.info("Checking for new photos for %s. The last update was: %s and the latest photo is: %s" % (flickr_user.username, datetime_last_update, last_upload.date_upload))
        if datetime_last_update and last_upload.date_upload == datetime_last_update:
            logger.info("No new photos for %s since last time." % (flickr_user.username))
            total_photos = flickr_user.count_photos_processed
            fetch_cameras = False
            
    except Photo.DoesNotExist:
        logger.info("Aww, %s doesn't have any photos." % (flickr_user.username))
        fetch_cameras = False
    
    if fetch_cameras:
        cameras = flickr_user.cameras.all()
        
        for camera in cameras:            
            logger.info("Updating camera %s for %s" % (camera, flickr_user.username))
        
            photos = Photo.objects.filter(camera=camera, owner_nsid=flickr_user.nsid)
        
            photos_count = photos.count()
            camera_last_upload = photos.latest('date_upload')
        
            if not datetime_last_update or camera_last_upload.date_upload > datetime_last_update:
                logger.info("Camera %s for %s may have new photos, updating" % (camera, flickr_user.username))
            
                first_taken = photos.order_by('date_taken')[:1].get()
                last_taken = photos.latest('date_taken')
                first_upload = photos.order_by('date_upload')[:1].get()
                comments_count = photos.aggregate(Sum('comments_count'))
                faves_count = photos.aggregate(Sum('faves_count'))
                
                FlickrUserCamera.objects.filter(camera=camera, flickr_user=flickr_user).update(
                    count_photos = photos_count,
                    date_first_taken = first_taken.date_taken,
                    first_taken_id = first_taken.photo_id,
                    date_first_upload = first_upload.date_upload,
                    first_upload_id = first_upload.photo_id,
                    date_last_taken = last_taken.date_taken,
                    last_taken_id = last_taken.photo_id,
                    date_last_upload = camera_last_upload.date_upload,
                    last_upload_id = camera_last_upload.photo_id,
                    comments_count = comments_count['comments_count__sum'],
                    faves_count = faves_count['faves_count__sum'],
                )
        
            total_photos = total_photos + photos_count
        
        last_upload_date = last_upload.date_upload
        flickr_user.date_last_photo_update = calendar.timegm(last_upload_date.timetuple())
        
        flickr_user.current_camera = flickr_user.calculate_current_camera()
        
    else:
        if not datetime_last_update:
            flickr_user.date_last_photo_update = 0
    
    flickr_user.count_photos_processed = total_photos
    flickr_user.count_cameras = flickr_user.cameras.count()
    flickr_user.initial_fetch_completed = True
        
    flickr_user.save()
    
    logger.info("Fetch for %s complete. That was fun!" % (flickr_user.username))
    
    logger.info("Dude, we're done here.")
    values = {
        'secret': settings.PUSHY_SECRET,
        'user_id': flickr_user.nsid,
        'message': simplejson.dumps({'type': 'fetch_photos.complete'}),
    }
    data = urllib.urlencode(values)
    req = urllib2.Request(settings.PUSHY_URL_LOCAL, data)
    response = urllib2.urlopen(req)
    
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
            FlickrUser.objects.filter(pk=flickr_user.pk).update(count_cameras=F('count_cameras')+1)
            
            logger.info("Push new camera.")
            values = {
                'secret': settings.PUSHY_SECRET,
                'user_id': flickr_user.nsid,
                'message': simplejson.dumps({'type': 'fetch_photos.new_camera', 'data': {'name': camera.name, 'user':flickr_user.slug, 'camera': camera.slug}}),
            }
            data = urllib.urlencode(values)
            req = urllib2.Request(settings.PUSHY_URL_LOCAL, data)
            response = urllib2.urlopen(req)
            
        else:
            logger.info("We've seen this camera (%s) for this user before, updating counts." % (camera))
            
            # Update counts
            FlickrUserCamera.objects.filter(pk=flickr_user_camera.pk).update(count_photos=F('count_photos')+1)
            
            if photo.comments_count:
                FlickrUserCamera.objects.filter(pk=flickr_user_camera.pk).update(comments_count=F('comments_count')+int(photo.comments_count))
                
            if photo.faves_count:
                FlickrUserCamera.objects.filter(pk=flickr_user_camera.pk).update(faves_count=F('faves_count')+int(photo.faves_count))
                
            fuzzy_count = flickr_user_camera.count_photos + 1
            
            if fuzzy_count % 5 == 0:            
                logger.info("Push camera photo count (fuzzy).")
                values = {
                    'secret': settings.PUSHY_SECRET,
                    'user_id': flickr_user.nsid,
                    'message': simplejson.dumps({'type': 'fetch_photos.camera_photo_count', 'data': {'camera': camera.slug, 'count': fuzzy_count}}),
                }
                data = urllib.urlencode(values)
                req = urllib2.Request(settings.PUSHY_URL_LOCAL, data)
                response = urllib2.urlopen(req)
            
        return
        
    return
    
@task
def fetch_contacts_for_flickr_user(nsid):
    logger.info("Fetching contacts for Flickr user %s." % (nsid))
    user = UserProfile.objects.get(flickr_nsid = nsid)
    flickr_user = user.flickr_user
    
    try:
        # Query Flickr for this user's contacts
        a = flickr_api.AuthHandler(access_token_key = str(user.flickr_oauth_token), access_token_secret = str(user.flickr_oauth_token_secret))
        flickr_api.set_auth_handler(a)

        rsp = flickr.contacts.getList(sort="time", format="json",nojsoncallback="true")
        json = simplejson.loads(rsp)
        
        if json and json['stat'] == 'ok':
            try:
                contacts = json['contacts']['contact']
            
                for contact in contacts:
                    logger.info("Contact! %s" % (contact['username']))
                
                    try:
                        contact = FlickrUser.objects.get(pk = contact['nsid'])
                        logger.info("Sweet, they're already here!")
                    
                        flickr_user_contact, created = FlickrUserContact.objects.get_or_create(flickr_user = flickr_user, contact = contact)
                    
                        if created and contact.date_last_photo_update:
                            logger.info("Push found contact.")
                            values = {
                                'secret': settings.PUSHY_SECRET,
                                'user_id': flickr_user.nsid,
                                'message': simplejson.dumps({'type': 'fetch_contacts.new_contact', 'data': {'contact': contact.slug}}),
                            }
                            data = urllib.urlencode(values)
                            req = urllib2.Request(settings.PUSHY_URL_LOCAL, data)
                            response = urllib2.urlopen(req)
                    
                    except FlickrUser.DoesNotExist:
                        logger.info("Bummer, they haven't been here yet.")
                    
                        flickr_contact_lookup, created = FlickrContactLookup.objects.get_or_create(
                            flickr_user = flickr_user,
                            nsid = contact['nsid'],
                            defaults = {
                                'username': contact['username'],
                                'iconserver': contact['iconserver'],
                                'iconfarm': contact['iconfarm'],
                            }
                        )
                    
                flickr_user.count_contacts = flickr_user.contacts.count()
                flickr_user.save()
                
            except KeyError:
                logger.info("Looks like this user doesn't have any contacts.")
                return
            
    except URLError, e:
        logger.error("Problem talking to Flickr (URLError), will try again. Reason: %s" % (e.reason))
        return fetch_contacts_for_flickr_user.retry(countdown=5)
    
@task
def process_new_flickr_user(nsid):
    logger.info("Sweet, a new user, lets update stuff!")
    flickr_user = FlickrUser.objects.get(nsid = nsid)
    
    # Update other people's contacts if they're waiting for this person
    contact_lookups = FlickrContactLookup.objects.filter(nsid = flickr_user.nsid)
    
    for contact_lookup in contact_lookups:
        logger.info("Hooray, %s will be so happy %s is here!" % (contact_lookup.flickr_user.username, flickr_user.username))
        updating_flickr_user = contact_lookup.flickr_user
        
        flickr_user_contact, created = FlickrUserContact.objects.get_or_create(flickr_user = updating_flickr_user, contact = flickr_user)
        
        updating_flickr_user.count_contacts = updating_flickr_user.contacts.count()
        updating_flickr_user.save()
        
        contact_lookup.delete()
        
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
    
    logger.info("Cleaning up contacts.")
    
    logger.info("Removing their contact lookups.")
    contact_lookups = FlickrContactLookup.objects.filter(flickr_user = flickr_user).all()
    contact_lookups.delete()
    
    logger.info("Removing their contacts.")
    contacts = FlickrUserContact.objects.filter(flickr_user = flickr_user).all()
    contacts.delete()
    
    logger.info("Removing this user from other users contacts.")
    reverse_contacts = FlickrUserContact.objects.filter(contact = flickr_user).all()
    
    for reverse_contact in reverse_contacts:
        logger.info("Putting them back into contact_lookup.")
        flickr_contact_lookup, created = FlickrContactLookup.objects.get_or_create(
            flickr_user = reverse_contact.flickr_user,
            nsid = flickr_user.nsid,
            defaults = {
                'username': flickr_user.username,
                'iconserver': flickr_user.iconserver,
                'iconfarm': flickr_user.iconfarm,
            }
        )
        
        reverse_contact.delete()
    
    if reset:
        flickr_user.count_photos_processed = None
        flickr_user.date_last_photo_update = None
        flickr_user.save()
    else:
        logger.info("Deleting Flickr user %s" % (nsid))
        flickr_user.delete()
        