from .auth import ScheduleUser
from .schedule import Lesson
from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=10)
    head = models.ForeignKey(ScheduleUser, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.SmallIntegerField(default=None, null=True)
    schedule = models.ManyToManyField(Lesson)