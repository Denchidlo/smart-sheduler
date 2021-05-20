from .auth import ScheduleUser
from django.db import models


class Chat(models.Model):
    chat_id = models.PositiveBigIntegerField(unique=True)
    connected_user = models.ForeignKey(
        to=ScheduleUser,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_DEFAULT,
    )
    state = models.PositiveBigIntegerField()
    authorised = models.BooleanField(default=False)

    @classmethod
    def get_chat(cls, chat_id):
        try:
            return cls.objects.get(chat_id=chat_id)
        except:
            return None

    def get_chatlist(self, group):
        chat_list = Chat.objects.filter(connected_user__group__name=group.name)
        return [el.chat_id for el in chat_list]
