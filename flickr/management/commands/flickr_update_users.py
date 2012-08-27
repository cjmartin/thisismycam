from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from flickr.tasks import update_flickr_users

class Command(BaseCommand):
    help = 'Update flickr users'

    def handle(self, *args, **options):
        
        update_flickr_users.delay(None)
        
        self.stdout.write("All Done!\n")