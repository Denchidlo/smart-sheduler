from http.client import HTTP_PORT
import time
from django.conf import settings
from django.http import HttpResponse
from django.views import View 
from telebot import TeleBot, types, logger
import logging

__author__ = '@schedulebase_bot'

if settings.DEBUG:
    logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

bot = TeleBot(settings.TOKEN)

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=f"{settings.DOMAIN}/bot/")

class BotResponcer(View):
    def __init__(self):
        self.update_id = None

    def get(self, request, *args, **kwargs):
        return HttpResponse("Bot is running")

    def post(self, request, *args, **kwargs):
        global update_id
        json_str = request.body.decode('UTF-8')
        update = types.Update.de_json(json_str)
        if BotResponcer.update_id != update.update_id:
            bot.process_new_updates([update])
            update_id = update.update_id
            
        return HttpResponse('')