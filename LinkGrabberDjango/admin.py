from django.contrib import admin
from django.contrib.auth.models import User
from .models import watched, Profile, favourite, FeatureRequest
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.



class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'User_Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class WatchedAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', "date")
    search_fields = ['user']

admin.site.register(watched, WatchedAdmin)

class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', "date")
    search_fields = ['user']

admin.site.register(favourite, FavouriteAdmin)

class FeatureAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', "getstatus", "date")
    search_fields = ['user']

admin.site.register(FeatureRequest, FeatureAdmin)