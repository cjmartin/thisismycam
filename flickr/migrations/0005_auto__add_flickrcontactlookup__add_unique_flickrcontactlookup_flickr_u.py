# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FlickrContactLookup'
        db.create_table('flickr_flickrcontactlookup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('flickr_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flickr.FlickrUser'])),
            ('nsid', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('iconserver', self.gf('django.db.models.fields.IntegerField')()),
            ('iconfarm', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('flickr', ['FlickrContactLookup'])

        # Adding unique constraint on 'FlickrContactLookup', fields ['flickr_user', 'nsid']
        db.create_unique('flickr_flickrcontactlookup', ['flickr_user_id', 'nsid'])

        # Adding model 'FlickrUserContact'
        db.create_table('flickr_flickrusercontact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('flickr_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['flickr.FlickrUser'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flickr.FlickrUser'])),
        ))
        db.send_create_signal('flickr', ['FlickrUserContact'])

        # Adding unique constraint on 'FlickrUserContact', fields ['flickr_user', 'contact']
        db.create_unique('flickr_flickrusercontact', ['flickr_user_id', 'contact_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'FlickrUserContact', fields ['flickr_user', 'contact']
        db.delete_unique('flickr_flickrusercontact', ['flickr_user_id', 'contact_id'])

        # Removing unique constraint on 'FlickrContactLookup', fields ['flickr_user', 'nsid']
        db.delete_unique('flickr_flickrcontactlookup', ['flickr_user_id', 'nsid'])

        # Deleting model 'FlickrContactLookup'
        db.delete_table('flickr_flickrcontactlookup')

        # Deleting model 'FlickrUserContact'
        db.delete_table('flickr_flickrusercontact')


    models = {
        'cameras.camera': {
            'Meta': {'object_name': 'Camera'},
            'amazon_image_response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'amazon_item_response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'amazon_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cameras.Category']", 'symmetrical': 'False'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'count_photos': ('django.db.models.fields.IntegerField', [], {}),
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
        'flickr.flickrcontactlookup': {
            'Meta': {'unique_together': "(('flickr_user', 'nsid'),)", 'object_name': 'FlickrContactLookup'},
            'flickr_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flickr.FlickrUser']"}),
            'iconfarm': ('django.db.models.fields.IntegerField', [], {}),
            'iconserver': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nsid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'flickr.flickruser': {
            'Meta': {'object_name': 'FlickrUser'},
            'cameras': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cameras.Camera']", 'through': "orm['flickr.FlickrUserCamera']", 'symmetrical': 'False'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['flickr.FlickrUser']", 'through': "orm['flickr.FlickrUserContact']", 'symmetrical': 'False'}),
            'count_photos_processed': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_last_photo_update': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'iconfarm': ('django.db.models.fields.IntegerField', [], {}),
            'iconserver': ('django.db.models.fields.IntegerField', [], {}),
            'nsid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'primary_key': 'True'}),
            'path_alias': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
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
        },
        'flickr.flickrusercontact': {
            'Meta': {'unique_together': "(('flickr_user', 'contact'),)", 'object_name': 'FlickrUserContact'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flickr.FlickrUser']"}),
            'flickr_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['flickr.FlickrUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['flickr']