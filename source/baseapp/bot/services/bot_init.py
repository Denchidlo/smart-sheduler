from django.conf import settings
from ..dbmodels.auth import ScheduleUser
import time
from telebot import TeleBot, logger
import logging

__author__ = '@schedulebase_bot'

if settings.DEBUG:
    logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.
    
    try:
        ScheduleUser.objects.get(username='admin')
    except:    
        ScheduleUser.objects.create_superuser("admin", "Чепуха", "Костлявая", "admin")

bot = TeleBot(settings.TOKEN)

settings.BOT = bot

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=f"{settings.DOMAIN}/bot/")
