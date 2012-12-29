from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from flickr.tasks import update_flickr_users

class Command(BaseCommand):
    help = 'Update flickr users'
    option_list = BaseCommand.option_list + (
        make_option('--all_photos',
        action='store_true',
        dest='all_photos',
        default=False,
        help='Update all photos, not just new ones.'),
    )
    
    def handle(self, *args, **options):
        
        if options['all_photos']:
            update_flickr_users.delay(None, 1, 1, True)
        else:
            update_flickr_users.delay(None, 1, 1, False)
        
        self.stdout.write("All Done!\n")