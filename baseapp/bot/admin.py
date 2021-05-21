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
admin.site.register(GroupLead)
admin.site.register(Lesson)
admin.site.register(StudentGroup)

if settings.DATA_UPLOAD and not settings.PROCEEDED:
    ScheduleProvider().load()

    for el in StudentGroup.objects.all():
        GroupLead.objects.get_or_create(group=el, defaults={"user": None})

    settings.PROCEEDED = True
