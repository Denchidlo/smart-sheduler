from .auth import ScheduleUser
from django.db import models

class Chat(models.Model):
    chat_id = models.PositiveBigIntegerField(unique=True)
    connected_user = models.ForeignKey(to=ScheduleUser, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT)
    state = models.PositiveBigIntegerField()
    authorised = models.BooleanField(default=False)