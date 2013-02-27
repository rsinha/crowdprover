from django.db import models
from django.utils import timezone

# Create your models here.

class Program(models.Model):
    source = models.CharField(max_length=200) #filename
    description = models.CharField(max_length=200) #description1
    pub_date = models.DateTimeField('date published') #date released

    def __unicode__(self):
        return self.source

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Invariant(models.Model):
    program = models.ForeignKey(Program) #this invariant is bound to a program
    content = models.CharField(max_length=500) #what is the invariant
    line = models.IntegerField(default=0) #line number at which this invariant holds
    author = models.CharField(max_length=40) #author name
    date = models.DateTimeField('date reported') #date at which the user entered this invariant

    def __unicode__(self):
        return self.content
