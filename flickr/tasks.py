from django.conf import settings
from django.utils import simplejson

from celery.task import task
from flickr_api.api import flickr

from flickr.models import FlickrPlace

@task(ignore_result=True)
def process_flickr_place(flickr_place_id):
    print "Fetching Flickr place for place id %s" % flickr_place_id
    place_rsp = flickr.places.resolvePlaceId(place_id=flickr_place_id,format="json",nojsoncallback="true")
    json = simplejson.loads(place_rsp)

    if json and json['stat'] == 'ok':
        flickr_place = FlickrPlace.objects.get(place_id = flickr_place_id)
        
        location = json['location']
        
        flickr_place.woeid = location['woeid']
        flickr_place.latitude = location['latitude']
        flickr_place.longitude = location['longitude']
        flickr_place.place_url = location['place_url']
        flickr_place.place_type = location['place_type']
        flickr_place.place_type_id = location['place_type_id']
        
        try:
            if location['name']:
                flickr_place.name = location['name']
        except:
            True
                    
        try:
            if location['timezone']:
                flickr_place.timezone = location['timezone']
        except:
            True
        
        try:
            if location['neighbourhood']:
                flickr_place.neighbourhood_place_id = location['neighbourhood']['place_id']
                flickr_place.neighbourhood_woeid = location['neighbourhood']['woeid']
                flickr_place.neighbourhood_latitude = location['neighbourhood']['latitude']
                flickr_place.neighbourhood_longitude = location['neighbourhood']['longitude']
                flickr_place.neighbourhood_place_url = location['neighbourhood']['place_url']
                flickr_place.neighbourhood_name = location['neighbourhood']['_content']
        except:
            True
        
        try:
            if location['locality']:
                flickr_place.locality_place_id = location['locality']['place_id']
                flickr_place.locality_woeid = location['locality']['woeid']
                flickr_place.locality_latitude = location['locality']['latitude']
                flickr_place.locality_longitude = location['locality']['longitude']
                flickr_place.locality_place_url = location['locality']['place_url']
                flickr_place.locality_name = location['locality']['_content']
        except:
            True
            
        try:
            if location['county']:
                flickr_place.county_place_id = location['county']['place_id']
                flickr_place.county_woeid = location['county']['woeid']
                flickr_place.county_latitude = location['county']['latitude']
                flickr_place.county_longitude = location['county']['longitude']
                flickr_place.county_place_url = location['county']['place_url']
                flickr_place.county_name = location['county']['_content']
        except:
            True
            
        try:
            if location['region']:
                flickr_place.region_place_id = location['region']['place_id']
                flickr_place.region_woeid = location['region']['woeid']
                flickr_place.region_latitude = location['region']['latitude']
                flickr_place.region_longitude = location['region']['longitude']
                flickr_place.region_place_url = location['region']['place_url']
                flickr_place.region_name = location['region']['_content']
        except:
            True
        
        try:
            if location['country']:
                flickr_place.country_place_id = location['country']['place_id']
                flickr_place.country_woeid = location['country']['woeid']
                flickr_place.country_latitude = location['country']['latitude']
                flickr_place.country_longitude = location['country']['longitude']
                flickr_place.country_place_url = location['country']['place_url']
                flickr_place.country_name = location['country']['_content']
        except:
            True
        
        flickr_place.save()