from .dbmodels.validators import validate_username
from .dbmodels.chat import Chat
from .dbmodels.states import State, onstate
from .dbmodels.auth import ScheduleUser
import time
from django.conf import settings
from django.http import HttpResponse
from django.views import View
from telebot import TeleBot, types, logger
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
def cmd_start_handler(message: types.Message):
    chat_id = message.chat.id
    current_chat, created = Chat.objects.get_or_create(chat_id=chat_id, defaults={
        'connected_user': None,
        'state': State.CHAT_STARTED.value
    })
    if created:
        bot.send_message(chat_id, 'Hello, {user}\nNice to meet you'.format(
            user=message.from_user.first_name))
    else:
        bot.send_message(chat_id, 'Welcome back, {user}!'.format(
            user=message.from_user.first_name))
    if current_chat.state == State.CHAT_STARTED.value and current_chat.connected_user == None:
        inline_action = types.InlineKeyboardMarkup()
        inline_singin_button = types.InlineKeyboardButton(
            "Sign in", callback_data="c_signin")
        inline_login_button = types.InlineKeyboardButton(
            "Log in", callback_data="c_login")
        inline_stayunauth_button = types.InlineKeyboardButton(
            "Stay anonimous 👻", callback_data="c_anonym")
        inline_action.row(inline_login_button, inline_singin_button)
        inline_action.row(inline_stayunauth_button)
        bot.send_message(chat_id, 'Choose the action',
                         reply_markup=inline_action)

@bot.callback_query_handler(lambda call: call.data == 'c_signin')
def button_signin(call: types.CallbackQuery):
    callback_message = call.message
    try:
        chat_id = callback_message.chat.id
        chat = Chat.objects.get(chat_id=chat_id)
        bot.send_message(chat_id, "Enter username:")
        chat.state = State.SIGNING_IN_UNAME.value
        chat.save()
    except Exception:
        bot.send_message(callback_message.chat.id,
                         "Something went wrong\nTry again")

@bot.callback_query_handler(lambda call: call.data == 'c_login')
def button_login(call: types.CallbackQuery):
    callback_message = call.message
    try:
        chat_id = callback_message.chat.id
        chat = Chat.objects.get(chat_id=chat_id)
        bot.send_message(chat_id, "Enter username:")
        chat.state = State.LOGING_IN_UNAME.value
        chat.save()
    except Exception as ex:
        bot.send_message(callback_message.chat.id,
                         "Something went wrong\nTry again")

@bot.message_handler(content_types=['text'], func=lambda message: onstate(message.chat.id, State.LOGING_IN_UNAME))
def login_username_input(message):
    message_input = message.text
    chat_id = message.chat.id
    chat = Chat.objects.get(chat_id=chat_id)
    try:
        user = ScheduleUser.objects.get(username=message_input)
        chat.connected_user = user
        chat.save()
    except Exception:
        user = None
    chat.state = State.LOGING_IN_PASS.value
    chat.save()
    bot.send_message(chat_id, "Enter password:")

@bot.message_handler(content_types=['text'], func=lambda message: onstate(message.chat.id, State.LOGING_IN_PASS))
def login_password_input(message):
    message_input = message.text
    chat_id = message.chat.id
    chat = Chat.objects.get(chat_id=chat_id)
    if chat.connected_user != None and chat.connected_user.check_password(message_input) == True:
        chat.authorised = True
        bot.send_message(chat_id, "Success!")
    else:
        chat.connected_user = None
        bot.send_message(chat_id, "Login failed!\nIvalid username or password")
    chat.state = State.NO_ACTIONS.value
    chat.save()

@bot.message_handler(content_types=['text'], func=lambda message: onstate(message.chat.id, State.SIGNING_IN_UNAME))
def signin_username_input(message):
    message_input = message.text
    chat_id = message.chat.id
    chat = Chat.objects.get(chat_id=chat_id)
    try:
        _ = ScheduleUser.objects.get(username=message_input)
        bot.send_message(chat_id, 'Username is used by somebody else!')
        chat.state = State.NO_ACTIONS.value
    except Exception:
        if validate_username(message_input):
            chat.state = State.SIGNING_IN_PASS.value
            # To Complete
            chat.connected_user = ScheduleUser.objects.create(message_input, )
            bot.send_message(chat_id, "Enter password:")
        else:
            chat.state = State.NO_ACTIONS.value
            bot.send_message(chat_id, "Username should contain from 5 to 30 digits/characters!")
        chat.save()

@bot.message_handler(content_types=['text'], func=lambda message: onstate(message.chat.id, State.LOGING_IN_PASS))
def signin_password_input(message):
    message_input = message.text
    chat_id = message.chat.id
    chat = Chat.objects.get(chat_id=chat_id)
    if chat.connected_user != None and chat.connected_user.check_password(message_input) == True:
        chat.authorised = True
        bot.send_message(chat_id, "Success!")
    else:
        chat.connected_user = None
        bot.send_message(chat_id, "Login failed!\nIvalid username or password")
    chat.state = State.NO_ACTIONS.value
    chat.save()