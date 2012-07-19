from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from flickr.models import FlickrUser

from photos.tasks import fetch_photos_for_flickr_user

class Command(BaseCommand):
    help = 'Fetch photos for a flickr user.'
    option_list = BaseCommand.option_list + (
        make_option('--user',
        action='store',
        dest='user',
        help='User (flickr) to fetch photos for.'),
    )

    def handle(self, *args, **options):
        user = FlickrUser.objects.get(nsid=options.get('user'))
        fetch_photos_for_flickr_user.delay(None, user.nsid)
        
        self.stdout.write("All Done!\n")