from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User

from django.db import models
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class watched(models.Model):
    user = models.CharField(max_length=100)
    epid = models.CharField(max_length=50)
    epname = models.CharField(max_length=100)
    showid = models.CharField(max_length=50)
    showname = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now, blank=True)
    """class Meta:
        unique_together = ["user", "epid", "showid"]"""
    def __str__(self):
        return self.user + " - " + self.epname

    def __unicode__(self):
        return self.user + " - " + self.epname


    def getdate(self):
        return self.date

class favourite(models.Model):
    user = models.CharField(max_length=100)
    showid = models.CharField(max_length=50)
    showname = models.CharField(max_length=100)
    show = models.BooleanField(default=True)
    newep = models.BooleanField(default=False)
    poster = models.CharField(max_length=300, default="")
    date = models.DateTimeField(default=timezone.now, blank=True)
    count = models.CharField(max_length=10)
    """class Meta:
        unique_together = ["user", "epid", "showid"]"""
    def __str__(self):
        return self.user + " - " + self.showname

    def __unicode__(self):
        return self.user + " - " + self.showname


    def getdate(self):
        return self.date


class FeatureRequest(models.Model):
    user = models.ForeignKey('auth.User')
    title = models.CharField(max_length=100, unique=True)
    body = models.TextField()
    state = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now, blank=True)
    """class Meta:
        unique_together = ["user", "epid", "showid"]"""
    def __str__(self):
        return self.user.username + " - " + self.title

    def __unicode__(self):
        return self.user.username + " - " + self.title

    def getstatus(self):
        if self.state == 0:
            return "Submitted"
        if self.state == 1:
            return "Denied"
        if self.state == 2:
            return "Work in Progress"
        if self.state == 3:
            return "Finished"


    def getdate(self):
        return self.date

class Profile(models.Model):
    user = models.OneToOneField(User, null=False)
    autoplaybest = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now, blank=True)
    night_mode = models.BooleanField(default=False)
    autoplaynext = models.BooleanField(default=False)



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()