from .auth import ScheduleUser
from django.db import models

class Chat(models.Model):
    chat_id = models.PositiveBigIntegerField(unique=True)
    connected_user = models.ForeignKey(to=ScheduleUser, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT)
    state = models.PositiveBigIntegerField()

    def connect_user(self, user: ScheduleUser):
        self.connected_user = user
        self.save()

    def remove_connection(self):
        self.connected_user = None
        self.save()

    def save(self, *args, **kwargs):
        super().save()