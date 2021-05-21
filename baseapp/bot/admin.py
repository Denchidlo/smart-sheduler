from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .services.modelprovider import ScheduleProvider
from .models import *
from threading import Thread
import os

admin.site.unregister(Group)
admin.site.register(ScheduleUser, UserAdmin)
admin.site.register(Chat)
admin.site.register(Employee)
admin.site.register(GroupLead)
admin.site.register(Lesson)
admin.site.register(StudentGroup)

if settings.DATA_UPLOAD and os.environ.get('RUN_MAIN') == 'true':
        temp_thread = Thread(target=ScheduleProvider().load, daemon=True)
        temp_thread.start()

