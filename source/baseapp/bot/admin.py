from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .services.modelprovider import ScheduleProvider
from .models import *

admin.site.unregister(Group)
admin.site.register(ScheduleUser, UserAdmin)
admin.site.register(Chat)
admin.site.register(Employee)
admin.site.register(Lesson)
admin.site.register(StudentGroup)

if settings.DATA_UPLOAD:
    ScheduleProvider().load()
