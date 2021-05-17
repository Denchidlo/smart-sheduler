from .auth import ScheduleUser
from django.db import models

class StudentGroup(models.Model):
    name = models.CharField(max_length=7, unique=True)
    head = models.ForeignKey(ScheduleUser, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.SmallIntegerField(default=None, null=True)