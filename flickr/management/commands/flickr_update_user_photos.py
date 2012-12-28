from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from django.utils import simplejson
from flickr_api.api import flickr

from flickr.models import FlickrUser

from flickr.tasks import update_photos_for_flickr_user

class Command(BaseCommand):
    help = 'Updatte photos for a flickr user.'
    option_list = BaseCommand.option_list + (
        make_option('--user',
        action='store',
        dest='user',
        help='User (flickr) to fetch photos for.'),
        make_option('--all',
        action='store_true',
        dest='all',
        default=False,
        help='Update all photos, not just new ones.'),
        )
    )

    def handle(self, *args, **options):
        user = FlickrUser.objects.get(nsid=options.get('user'))
        
        rsp = flickr.people.getInfo(user_id=user.nsid,format="json",nojsoncallback="true")
        json = simplejson.loads(rsp)

        if json and json['stat'] == "ok":
            api_user = json['person']
            
            user.count_photos = api_user['photos']['count']['_content']
            user.save()
            
        if options['all']:
            update_photos_for_flickr_user(None, user.nsid, None, True)
        else:
            update_photos_for_flickr_user.delay(None, user.nsid)
        
        self.stdout.write("All Done!\n")