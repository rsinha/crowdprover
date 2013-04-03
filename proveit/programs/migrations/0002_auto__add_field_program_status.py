# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Program.status'
        db.add_column('programs_program', 'status',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Program.status'
        db.delete_column('programs_program', 'status')


    models = {
        'programs.invariant': {
            'Meta': {'object_name': 'Invariant'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['programs.Program']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'programs.loopinvariant': {
            'Meta': {'object_name': 'LoopInvariant'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loopId': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['programs.Program']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'programs.program': {
            'Meta': {'object_name': 'Program'},
            'binary': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['programs']