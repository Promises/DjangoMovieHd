from django.contrib import admin
from django.contrib.auth.models import User
from .models import watched, Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

admin.site.register(watched)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'User_Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )
admin.site.unregister(User)
admin.site.register(User, UserAdmin)