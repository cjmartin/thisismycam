# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'FlickrUserCamera.date_first_upload'
        db.alter_column('flickr_flickrusercamera', 'date_first_upload', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'FlickrUserCamera.date_last_upload'
        db.alter_column('flickr_flickrusercamera', 'date_last_upload', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'FlickrUserCamera.last_upload_id'
        db.alter_column('flickr_flickrusercamera', 'last_upload_id', self.gf('django.db.models.fields.BigIntegerField')(null=True))

        # Changing field 'FlickrUserCamera.count_photos'
        db.alter_column('flickr_flickrusercamera', 'count_photos', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'FlickrUserCamera.date_last_taken'
        db.alter_column('flickr_flickrusercamera', 'date_last_taken', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'FlickrUserCamera.last_taken_id'
        db.alter_column('flickr_flickrusercamera', 'last_taken_id', self.gf('django.db.models.fields.BigIntegerField')(null=True))

        # Changing field 'FlickrUserCamera.first_taken_id'
        db.alter_column('flickr_flickrusercamera', 'first_taken_id', self.gf('django.db.models.fields.BigIntegerField')(null=True))

        # Changing field 'FlickrUserCamera.date_first_taken'
        db.alter_column('flickr_flickrusercamera', 'date_first_taken', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'FlickrUserCamera.first_upload_id'
        db.alter_column('flickr_flickrusercamera', 'first_upload_id', self.gf('django.db.models.fields.BigIntegerField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'FlickrUserCamera.date_first_upload'
        raise RuntimeError("Cannot reverse this migration. 'FlickrUserCamera.date_first_upload' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'FlickrUserCamera.date_last_upload'
        raise RuntimeError("Cannot reverse this migration. 'FlickrUserCamera.date_last_upload' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'FlickrUserCamera.last_upload_id'
        raise RuntimeError("Cannot reverse this migration. 'FlickrUserCamera.last_upload_id' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'FlickrUserCamera.count_photos'
        raise RuntimeError("Cannot reverse this migration. 'FlickrUserCamera.count_photos' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'FlickrUserCamera.date_last_taken'
        raise RuntimeError("Cannot reverse this migration. 'FlickrUserCamera.date_last_taken' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'FlickrUserCamera.last_taken_id'
        raise RuntimeError("Cannot reverse this migration. 'FlickrUserCamera.last_taken_id' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'FlickrUserCamera.first_taken_id'
        raise RuntimeError("Cannot reverse this migration. 'FlickrUserCamera.first_taken_id' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'FlickrUserCamera.date_first_taken'
        raise RuntimeError("Cannot reverse this migration. 'FlickrUserCamera.date_first_taken' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'FlickrUserCamera.first_upload_id'
        raise RuntimeError("Cannot reverse this migration. 'FlickrUserCamera.first_upload_id' and its values cannot be restored.")

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
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
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
            'Meta': {'unique_together': "(('flickr_user', 'camera'),)", 'object_name': 'FlickrUserCamera'},
            'camera': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cameras.Camera']"}),
            'comments_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'count_photos': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_first_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_first_upload': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_last_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_last_upload': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'faves_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'first_taken_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'first_upload_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flickr_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flickr.FlickrUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_taken_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_upload_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['flickr']