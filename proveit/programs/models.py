from django.db import models
from django.utils import timezone

# Create your models here.

class Program(models.Model):
    source = models.CharField(max_length=200) #filename
    binary = models.CharField(max_length=200) #binary name
    description = models.CharField(max_length=200) #description
    pub_date = models.DateTimeField('date published') #date released

    def __unicode__(self):
        return self.description

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Invariant(models.Model):
    program = models.ForeignKey(Program) #this invariant is bound to a program
    content = models.CharField(max_length=500) #what is the invariant
    line = models.IntegerField(default=0) #line number at which this invariant holds
    status = models.IntegerField(default=0) #UNKNOWN=0, YES=1, NO=2, AXIOM=3
    author = models.CharField(max_length=40) #author name
    date = models.DateTimeField('date reported') #date at which the user entered this invariant

    def __unicode__(self):
        return self.content

class LoopInvariant(models.Model):
    program = models.ForeignKey(Program) #this invariant is bound to a program
    content = models.CharField(max_length=500) #what is the invariant
    loopId = models.IntegerField(default=0) #which loop in the program this loop invariant applies to
    status = models.IntegerField(default=0) #UNKNOWN=0, YES=1, NO=2, AXIOM=3
    author = models.CharField(max_length=40) #author name
    date = models.DateTimeField('date reported') #date at which the user entered this invariant

    def __unicode__(self):
        return self.content

