# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Photo'
        db.create_table('photos_photo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('photo_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('server', self.gf('django.db.models.fields.IntegerField')()),
            ('farm', self.gf('django.db.models.fields.IntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('license', self.gf('django.db.models.fields.IntegerField')()),
            ('media', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('owner_nsid', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('owner_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('path_alias', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('date_taken', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_upload', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_create', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('camera', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cameras.Camera'])),
            ('camera_make', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cameras.Make'], null=True, blank=True)),
        ))
        db.send_create_signal('photos', ['Photo'])


    def backwards(self, orm):
        # Deleting model 'Photo'
        db.delete_table('photos_photo')


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
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'})
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
        'photos.photo': {
            'Meta': {'object_name': 'Photo'},
            'camera': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cameras.Camera']"}),
            'camera_make': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cameras.Make']", 'null': 'True', 'blank': 'True'}),
            'date_create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_upload': ('django.db.models.fields.DateTimeField', [], {}),
            'farm': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.IntegerField', [], {}),
            'media': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner_nsid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path_alias': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'photo_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'server': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['photos']