from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from flickr.models import FlickrUser

class Command(BaseCommand):
    help = 'Clears all cameras and photos stored for a Flickr user.'
    option_list = BaseCommand.option_list + (
        make_option('--user',
        action='store',
        dest='user',
        help='User (flickr) update.'),
    )

    def handle(self, *args, **options):
        flickr_user = FlickrUser.objects.get(nsid=options.get('user'))
        
        flickr_user.current_camera = flickr_user.calculate_current_camera()
        
        self.stdout.write("Setting current camera for %s to %s" % (flickr_user.username, flickr_user.current_camera.camera.name))
        flickr_user.save()
        
        self.stdout.write("All Done!\n")