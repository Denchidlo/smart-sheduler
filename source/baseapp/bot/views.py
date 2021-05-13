from http.client import HTTP_PORT
import time
from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
from django.views import View 
from telebot import TeleBot, types, logger
import logging

import telebot

bot = TeleBot(settings.TOKEN)

logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

__author__ = '@schedulebase_bot'

update_id = None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

class BotResponcer(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Bot is running")

    def post(self, request, *args, **kwargs):
        global update_id
        json_str = request.body.decode('UTF-8')
        print("New object")
        update = types.Update.de_json(json_str)
        print(dir(update.message))
        print(update.message.text)
        print(f"Prev id:{update_id}\nnew id:{update.update_id}")
        if update_id != update.update_id:
            bot.process_new_updates([update])
            update_id = update.update_id
 
        return HttpResponse('')

 


# Webhook
bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=f"{settings.DOMAIN}/bot/")