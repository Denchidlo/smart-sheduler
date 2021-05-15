from .dbmodels.validators import validate_username
from .dbmodels.chat import Chat
from .dbmodels.states import State, onstate
from .dbmodels.auth import ScheduleUser
from .handlers import login, signin
from .bot_init import bot
from django.http import HttpResponse
from django.views import View
from telebot import types
from .bot_init import bot

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
    if current_chat.authorised == False and current_chat.connected_user == None:
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

