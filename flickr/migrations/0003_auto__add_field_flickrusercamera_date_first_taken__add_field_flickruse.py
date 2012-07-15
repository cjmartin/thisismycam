# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'FlickrUserCamera.date_first_taken'
        db.add_column('flickr_flickrusercamera', 'date_first_taken', self.gf('django.db.models.fields.DateTimeField')(default='2012-07-15 06:49:47.530465'), keep_default=False)

        # Adding field 'FlickrUserCamera.date_last_taken'
        db.add_column('flickr_flickrusercamera', 'date_last_taken', self.gf('django.db.models.fields.DateTimeField')(default='2012-07-15 06:49:47.530465'), keep_default=False)

        # Adding field 'FlickrUserCamera.date_first_upload'
        db.add_column('flickr_flickrusercamera', 'date_first_upload', self.gf('django.db.models.fields.DateTimeField')(default='2012-07-15 06:49:47.530465'), keep_default=False)

        # Adding field 'FlickrUserCamera.date_last_upload'
        db.add_column('flickr_flickrusercamera', 'date_last_upload', self.gf('django.db.models.fields.DateTimeField')(default='2012-07-15 06:49:47.530465'), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'FlickrUserCamera.date_first_taken'
        db.delete_column('flickr_flickrusercamera', 'date_first_taken')

        # Deleting field 'FlickrUserCamera.date_last_taken'
        db.delete_column('flickr_flickrusercamera', 'date_last_taken')

        # Deleting field 'FlickrUserCamera.date_first_upload'
        db.delete_column('flickr_flickrusercamera', 'date_first_upload')

        # Deleting field 'FlickrUserCamera.date_last_upload'
        db.delete_column('flickr_flickrusercamera', 'date_last_upload')


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
            'make': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cameras.Make']", 'null': 'True', 'blank': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
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
            'count_photos': ('django.db.models.fields.IntegerField', [], {}),
            'date_first_taken': ('django.db.models.fields.DateTimeField', [], {}),
            'date_first_upload': ('django.db.models.fields.DateTimeField', [], {}),
            'date_last_taken': ('django.db.models.fields.DateTimeField', [], {}),
            'date_last_upload': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'flickr_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flickr.FlickrUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['flickr']
