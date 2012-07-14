# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FlickrUser'
        db.create_table('flickr_flickruser', (
            ('nsid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('realname', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('path_alias', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('iconserver', self.gf('django.db.models.fields.IntegerField')()),
            ('iconfarm', self.gf('django.db.models.fields.IntegerField')()),
            ('count_photos_processed', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_last_photo_update', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_create', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('flickr', ['FlickrUser'])


    def backwards(self, orm):
        # Deleting model 'FlickrUser'
        db.delete_table('flickr_flickruser')


    models = {
        'flickr.flickruser': {
            'Meta': {'object_name': 'FlickrUser'},
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
        }
    }

    complete_apps = ['flickr']