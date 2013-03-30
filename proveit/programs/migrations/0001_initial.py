# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Program'
        db.create_table('programs_program', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('binary', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('programs', ['Program'])

        # Adding model 'Invariant'
        db.create_table('programs_invariant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('program', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['programs.Program'])),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('line', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('programs', ['Invariant'])

        # Adding model 'LoopInvariant'
        db.create_table('programs_loopinvariant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('program', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['programs.Program'])),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('loopId', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('programs', ['LoopInvariant'])


    def backwards(self, orm):
        # Deleting model 'Program'
        db.delete_table('programs_program')

        # Deleting model 'Invariant'
        db.delete_table('programs_invariant')

        # Deleting model 'LoopInvariant'
        db.delete_table('programs_loopinvariant')


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
            'source': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['programs']