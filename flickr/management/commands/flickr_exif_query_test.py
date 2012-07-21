from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from django.utils import simplejson
from flickr_api.api import flickr
from flickr_api.base import FlickrError
from urllib2 import URLError

from photos.tasks import clean_make, clean_model

class Command(BaseCommand):
    help = 'Fetch photos for a flickr user.'
    option_list = BaseCommand.option_list + (
        make_option('--photo',
        action='store',
        dest='photo',
        help='Photo id to fetch Exif for.'),
    )

    def handle(self, *args, **options):
        
        self.stdout.write("Processing photo %s" % (options.get('photo')))

        try:
            # Query Flickr for this photo's Exif data
            exif_rsp = flickr.photos.getExif(photo_id=options.get('photo'),format="json",nojsoncallback="true")
            exif = simplejson.loads(exif_rsp)

            # If it exists, process it
            if exif and exif['stat'] == 'ok':
                exif_camera = ""
                raw_exif_make = ""
                exif_make = ""
                raw_exif_model = ""
                exif_model = ""
                exif_software = ""

                for tag in exif['photo']['exif']:
                    if tag['label'] == "Make":
                        raw_exif_make = tag['raw']['_content']
                        self.stdout.write("Raw make: '%s'" % (raw_exif_make))
                        
                        exif_make = clean_make(tag['raw']['_content'])
                        self.stdout.write("Clean make: '%s'" % (exif_make))

                    if tag['label'] == "Model":
                        raw_exif_model = tag['raw']['_content']
                        self.stdout.write("Raw model: '%s'" % (raw_exif_model))
                        
                        exif_model = clean_model(tag['raw']['_content'], exif_make)
                        self.stdout.write("Clean model: '%s'" % (exif_model))
                        
                    if tag['label'] == "Software" :
                        exif_software = tag['raw']['_content']
                        
                # This is the "name" that Flickr uses, it's usually nice
                if exif['photo']['camera']:
                    exif_camera = exif['photo']['camera']
                    self.stdout.write("Flickr name: %s" % (exif_camera))

                # If there's a model (camera) we'll carry on
                if exif_model:

                    # Create the camera slug with things that should never change
                    # I would use exif_camera, but I'm afraid those might change on Flickr's side
                    camera_slug = slugify(exif_make + " " + exif_model)
                    self.stdout.write("Camera slug: %s created using make: %s and model: %s" % (camera_slug, exif_make, exif_model))

                    # If the nice name doesn't exist, create one
                    if not exif_camera:
                        if exif_make:
                            exif_camera = exif_make + " " + exif_model
                        else:
                            exif_camera = exif_model
                            
                        self.stdout.write("There was no Flickr name, so one was created: %s" % (exif_camera))
                            
                    if exif_make:
                        make_slug = slugify(exif_make)
                        self.stdout.write("Make slug: %s" % (make_slug))

                # The photo doesn't have camera info
                else:
                    self.stdout.write("The photo doesn't have enough Exif to create a camera entry.")

        except URLError:
            logger.error("Problem talking to Flickr (URLError).")

        except FlickrError, e:
            logger.error("Problem talking to Flickr (FlickrError).\nError: %s" % (e))