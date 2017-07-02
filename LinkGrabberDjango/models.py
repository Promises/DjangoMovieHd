from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User

from django.db import models
import datetime
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class watched(models.Model):
    user = models.CharField(max_length=100)
    epid = models.CharField(max_length=50)
    epname = models.CharField(max_length=100)
    showid = models.CharField(max_length=50)
    showname = models.CharField(max_length=100)
    """class Meta:
        unique_together = ["user", "epid", "showid"]"""
    def __str__(self):
        return self.user + " - " + self.epname

class Profile(models.Model):
    user = models.OneToOneField(User, null=False)
    autoplaybest = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()