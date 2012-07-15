# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'FlickrPlace.longitude'
        db.alter_column('flickr_flickrplace', 'longitude', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'FlickrPlace.place_url'
        db.alter_column('flickr_flickrplace', 'place_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'FlickrPlace.woeid'
        db.alter_column('flickr_flickrplace', 'woeid', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'FlickrPlace.latitude'
        db.alter_column('flickr_flickrplace', 'latitude', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'FlickrPlace.place_type_id'
        db.alter_column('flickr_flickrplace', 'place_type_id', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'FlickrPlace.name'
        db.alter_column('flickr_flickrplace', 'name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'FlickrPlace.place_type'
        db.alter_column('flickr_flickrplace', 'place_type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))


    def backwards(self, orm):
        
        # Changing field 'FlickrPlace.longitude'
        db.alter_column('flickr_flickrplace', 'longitude', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'FlickrPlace.place_url'
        db.alter_column('flickr_flickrplace', 'place_url', self.gf('django.db.models.fields.CharField')(default=0, max_length=255))

        # Changing field 'FlickrPlace.woeid'
        db.alter_column('flickr_flickrplace', 'woeid', self.gf('django.db.models.fields.IntegerField')(default=0))

        # Changing field 'FlickrPlace.latitude'
        db.alter_column('flickr_flickrplace', 'latitude', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'FlickrPlace.place_type_id'
        db.alter_column('flickr_flickrplace', 'place_type_id', self.gf('django.db.models.fields.IntegerField')(default=0))

        # Changing field 'FlickrPlace.name'
        db.alter_column('flickr_flickrplace', 'name', self.gf('django.db.models.fields.CharField')(default=0, max_length=255))

        # Changing field 'FlickrPlace.place_type'
        db.alter_column('flickr_flickrplace', 'place_type', self.gf('django.db.models.fields.CharField')(default=0, max_length=255))


    models = {
        'cameras.camera': {
            'Meta': {'object_name': 'Camera'},
            'amazon_image_response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'amazon_item_response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'amazon_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cameras.Category']", 'symmetrical': 'False'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'date_create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'exif_make': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'exif_model': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'large_photo_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'make': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cameras.Make']", 'null': 'True', 'blank': 'True'}),
            'medium_photo_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'small_photo_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'cameras.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'cameras.make': {
            'Meta': {'object_name': 'Make'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'flickr.flickrplace': {
            'Meta': {'object_name': 'FlickrPlace'},
            'country_latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'country_longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'country_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country_place_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country_place_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country_woeid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'county_latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'county_longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'county_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'county_place_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'county_place_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'county_woeid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'locality_latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'locality_longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'locality_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'locality_place_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'locality_place_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'locality_woeid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'neighbourhood_latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'neighbourhood_longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'neighbourhood_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'neighbourhood_place_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'neighbourhood_place_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'neighbourhood_woeid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'place_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'primary_key': 'True'}),
            'place_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'place_type_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'place_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'region_latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'region_longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'region_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'region_place_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'region_place_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'region_woeid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'woeid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'flickr.flickruser': {
            'Meta': {'object_name': 'FlickrUser'},
            'cameras': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cameras.Camera']", 'through': "orm['flickr.FlickrUserCamera']", 'symmetrical': 'False'}),
            'count_photos_processed': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_last_photo_update': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'iconfarm': ('django.db.models.fields.IntegerField', [], {}),
            'iconserver': ('django.db.models.fields.IntegerField', [], {}),
            'nsid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'primary_key': 'True'}),
            'path_alias': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'realname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'flickr.flickrusercamera': {
            'Meta': {'object_name': 'FlickrUserCamera'},
            'camera': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cameras.Camera']"}),
            'comments_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'count_photos': ('django.db.models.fields.IntegerField', [], {}),
            'date_first_taken': ('django.db.models.fields.DateTimeField', [], {}),
            'date_first_upload': ('django.db.models.fields.DateTimeField', [], {}),
            'date_last_taken': ('django.db.models.fields.DateTimeField', [], {}),
            'date_last_upload': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'faves_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'first_taken_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'first_upload_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'flickr_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flickr.FlickrUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_taken_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'last_upload_id': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['flickr']
