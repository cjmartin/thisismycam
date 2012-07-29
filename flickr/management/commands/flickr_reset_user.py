from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from photos.tasks import delete_flickr_user

class Command(BaseCommand):
    help = 'Clears all cameras and photos stored for a Flickr user.'
    option_list = BaseCommand.option_list + (
        make_option('--user',
        action='store',
        dest='user',
        help='User (flickr) to reset.'),
    )

    def handle(self, *args, **options):
        delete_flickr_user.delay(options.get('user'), True)
        
        self.stdout.write("All Done!\n")