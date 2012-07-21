from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from django.utils import simplejson
from flickr_api.api import flickr

class Command(BaseCommand):
    help = 'Fetch photos for a flickr user.'
    option_list = BaseCommand.option_list + (
        make_option('--photo',
        action='store',
        dest='photo',
        help='Photo id to fetch Exif for.'),
    )

    def handle(self, *args, **options):
        exif_rsp = flickr.photos.getExif(photo_id=options.get('photo'),format="json",nojsoncallback="true")
        
        self.stdout.write(exif_rsp)
        
        self.stdout.write("All Done!\n")