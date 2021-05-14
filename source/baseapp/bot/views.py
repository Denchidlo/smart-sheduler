from .dbmodels.chat import Chat
from .dbmodels.states import State
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

settings.BOT = bot

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
        if self.update_id != update.update_id:
            bot.process_new_updates([update])
            update_id = update.update_id
            
        return HttpResponse('')

# Set some views
@bot.message_handler(commands=['start'])
def start_chat(message):
    chat_id = message.chat.id
    current_chat, created = Chat.objects.get_or_create(chat_id=chat_id, defaults={
        'connected_user': None,
        'state': State.CHAT_STARTED.value 
        })
    if created:
        bot.send_message(chat_id, 'Hello, {user}\nNice to meet you'.format(user=message.from_user.first_name))
    else:
        bot.send_message(chat_id, 'Welcome back, {user}!'.format(user=message.from_user.first_name))
    if current_chat.state == State.CHAT_STARTED.value and current_chat.connected_user == None:
        inline_action = types.InlineKeyboardMarkup()
        inline_register_button = types.InlineKeyboardButton("Register ➡️", callback_data="c_register")
        inline_stayunauth_button = types.InlineKeyboardButton("Stay anonimous 👻", callback_data="c_anonym")
        inline_action.row(inline_register_button)
        inline_action.row(inline_stayunauth_button)
        bot.send_message(chat_id, 'Choose the action', reply_markup=inline_action)
         