from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from datetime import datetime
from django.utils import timezone

from flickr.models import FlickrUser
from photos.models import Photo

class Command(BaseCommand):
    help = 'Debug flickr user update dates'

    def handle(self, *args, **options):
        
        flickr_users = FlickrUser.objects.order_by('date_create')
        
        for flickr_user in flickr_users:
            datetime_last_update = datetime.utcfromtimestamp(float(flickr_user.date_last_photo_update)).replace(tzinfo=timezone.utc)
            
            try:
                last_upload = Photo.objects.filter(owner_nsid=flickr_user.nsid).latest('date_upload')
                #self.stdout.write("Awesome, %s user has photos!\n" % (flickr_user.username))

                #self.stdout.write("Checking for new photos for %s. The last update was: %s and the latest photo is: %s\n" % (flickr_user.username, datetime_last_update, last_upload.date_upload))
                if last_upload.date_upload != datetime_last_update:
                    self.stdout.write("%s | last photo: %s | last update: %s\n" % (flickr_user.username, last_upload.date_upload, datetime_last_update))

            except Photo.DoesNotExist:
                self.stdout.write("%s doesn't have any photos" % (flickr_user.username))
        
        self.stdout.write("All Done!\n")