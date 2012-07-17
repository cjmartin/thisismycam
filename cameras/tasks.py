from django.conf import settings
from django.utils import simplejson

from celery.task import task

from cameras.models import Camera

import bottlenose
import urllib2 as urllib

@task(ignore_result=True)
def add_aws_item_to_camera(camera_id):
    camera = Camera.objects.get(pk = camera_id)
    aws_items = get_aws_items(camera)

    if aws_items:
        camera.amazon_item_response = simplejson.dumps(aws_items[0])

        # Clean up and add the item url
        url = urllib.unquote(aws_items[0]['DetailPageURL'])
        split_url = url.split('?')
        pretty_url = split_url[0] + "?tag=" + settings.AWS_ASSOCIATE_TAG

        camera.amazon_url = pretty_url

        # Lets go ahead and try to get images too, saving a write later
        aws_photos = get_aws_photos_for_item(aws_items[0])

        if aws_photos:
            camera.amazon_image_response = simplejson.dumps(aws_photos)
    
            if aws_photos[0]['LargeImage']['URL']:
                camera.large_photo_url = aws_photos[0]['LargeImage']['URL']
        
            if aws_photos[0]['MediumImage']['URL']:
                camera.medium_photo_url = aws_photos[0]['MediumImage']['URL']
        
            if aws_photos[0]['SmallImage']['URL']:
                camera.small_photo_url = aws_photos[0]['SmallImage']['URL']

        camera.save()
            
    return
        
@task(ignore_result=True)
def add_aws_photos_to_camera(camera_id):
    camera = Camera.opjects.get(pk = camera_id)
    aws_item = simplejson.loads(camera.amazon_item_response)

    if aws_item:
        aws_photos = get_aws_photos_for_item(aws_item)

        if aws_photos:
            camera.amazon_image_response = simplejson.dumps(aws_photos)
            camera.save()
            
def get_aws_items(camera):
    #print "Fetching Amazon items for camera %s.\n" % camera.name
    amazon = bottlenose.Amazon(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_ASSOCIATE_TAG)

    try :
        aws_res = amazon.ItemSearch(SearchIndex="Electronics", Manufacturer=camera.make, Keywords=camera.model, Style="http://resources.cjmart.in/xml2json.xslt")

        aws_search_res = simplejson.loads(aws_res)
        aws_item = aws_search_res['ItemSearchResponse']['Items']['Item']

        try :
            # If there is only one item, aws_items will be the item.
            aws_title = aws_item['ItemAttributes']['Title']
            aws_items = [aws_item]

        except Exception, e :
            aws_items = aws_item

        return aws_items

    except Exception, e :
        return None

def get_aws_photos_for_item(item):
    #print "Fetching photos for Amazon item %s.\n" % item['ASIN']
    amazon = bottlenose.Amazon(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_ASSOCIATE_TAG)

    try:
        aws_res = amazon.ItemLookup(ResponseGroup="Images", ItemId=item['ASIN'], Style="http://resources.cjmart.in/xml2json.xslt")
        aws_photos_res = simplejson.loads(aws_res)

        try:
            image_sets = [aws_photos_res['ItemLookupResponse']['Items']['Item']['ImageSets']['ImageSet']]
        except Exception, e:
            try:
                image_sets = aws_photos_res['ItemLookupResponse']['Items']['Item']['ImageSets']
            except Exception, e:
                image_sets = None

        if not image_sets:
            try:
                image_sets = [aws_photos_res['ItemLookupResponse']['Items']['Item']]
            except Exception, e :
                image_sets = None

        return image_sets

    except Exception, e :
        return None

def get_aws_info (camera):
    amazon = bottlenose.Amazon(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_ASSOCIATE_TAG)

    aws_items = get_aws_items(camera)
    #print simplejson.dumps(aws_items[0])
    #print aws_items

    if aws_items:
        i = 0
        for item in aws_items :
            aws_items[i]['DetailPageURL'] = urllib.unquote(item['DetailPageURL'])
            aws_items[i]['image_sets'] = get_aws_photos_for_item(item)
            #print aws_items[i]['image_sets']

            try :
                aws_res = amazon.ItemLookup(ResponseGroup="Reviews", ItemId=item['ASIN'], Style="http://resources.cjmart.in/xml2json.xslt")
                aws_rev_res = simplejson.loads(aws_res)

                reviews_url = aws_rev_res['ItemLookupResponse']['Items']['Item']['CustomerReviews']['IFrameURL']

                if aws_rev == None :
                    aws_rev = reviews_url
                    reviews = urllib2.urlopen(reviews_url)
                    review_soup = BeautifulSoup(reviews)
                    review_html = str(review_soup.html.body.div)
                    # print(review_soup.prettify())

            except Exception, e :
                reviews_url = None

            i+=1

        #print aws_url
        #print simplejson.dumps(aws_items[0]['image_sets'])

        return aws_items

    else:
        return None