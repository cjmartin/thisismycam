from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from flickr.models import FlickrUser

class Command(BaseCommand):
    help = 'Backfill for initial fetch status'

    def handle(self, *args, **options):
        flickr_users = FlickrUser.objects.all()
        users_to_update = []
        
        for flickr_user in flickr_users:
            if flickr_user.date_last_photo_update:            
                flickr_user.initial_fetch_completed = True
        
                self.stdout.write("Setting initial fetch completed for %s\n" % (flickr_user.username))
                flickr_user.save()
            else:
                users_to_update.append(flickr_user)
                self.stdout.write("Scheduling %s for an update\n" % (flickr_user.username))
        
        self.stdout.write("All Done!\n")