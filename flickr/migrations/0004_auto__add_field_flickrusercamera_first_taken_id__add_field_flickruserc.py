# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'FlickrUserCamera.first_taken_id'
        db.add_column('flickr_flickrusercamera', 'first_taken_id', self.gf('django.db.models.fields.BigIntegerField')(default=0), keep_default=False)

        # Adding field 'FlickrUserCamera.last_taken_id'
        db.add_column('flickr_flickrusercamera', 'last_taken_id', self.gf('django.db.models.fields.BigIntegerField')(default=0), keep_default=False)

        # Adding field 'FlickrUserCamera.first_upload_id'
        db.add_column('flickr_flickrusercamera', 'first_upload_id', self.gf('django.db.models.fields.BigIntegerField')(default=0), keep_default=False)

        # Adding field 'FlickrUserCamera.last_upload_id'
        db.add_column('flickr_flickrusercamera', 'last_upload_id', self.gf('django.db.models.fields.BigIntegerField')(default=0), keep_default=False)

        # Adding field 'FlickrUserCamera.comments_count'
        db.add_column('flickr_flickrusercamera', 'comments_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'FlickrUserCamera.faves_count'
        db.add_column('flickr_flickrusercamera', 'faves_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'FlickrUserCamera.first_taken_id'
        db.delete_column('flickr_flickrusercamera', 'first_taken_id')

        # Deleting field 'FlickrUserCamera.last_taken_id'
        db.delete_column('flickr_flickrusercamera', 'last_taken_id')

        # Deleting field 'FlickrUserCamera.first_upload_id'
        db.delete_column('flickr_flickrusercamera', 'first_upload_id')

        # Deleting field 'FlickrUserCamera.last_upload_id'
        db.delete_column('flickr_flickrusercamera', 'last_upload_id')

        # Deleting field 'FlickrUserCamera.comments_count'
        db.delete_column('flickr_flickrusercamera', 'comments_count')

        # Deleting field 'FlickrUserCamera.faves_count'
        db.delete_column('flickr_flickrusercamera', 'faves_count')


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
