from .handlers import authorised, unauthorised, login, signin, groups, schedule, account
import logging
from .dbmodels.validators import validate_username
from .dbmodels.chat import Chat
from .dbmodels.states import State, onstate
from .dbmodels.auth import ScheduleUser
from .services.bot_init import bot
from django.http import HttpResponse
from django.views import View
from telebot import types


class BotResponcer(View):  # pragma: no cover
    def __init__(self):
        self.update_id = None

    def get(self, request, *args, **kwargs):
        return HttpResponse("Bot is running")

    def post(self, request, *args, **kwargs):
        json_str = request.body.decode("UTF-8")
        update = types.Update.de_json(json_str)
        logging.debug("NEW POST REQUEST")
        if self.update_id != update.update_id:
            bot.process_new_updates([update])
            self.update_id = update.update_id

        return HttpResponse("OK")


@bot.message_handler(commands=["start"])
def cmd_start_handler(message: types.Message):
    chat_id = message.chat.id
    current_chat, created = Chat.objects.get_or_create(
        chat_id=chat_id,
        defaults={
            "connected_user": None,
            "state": State.CHAT_STARTED.value,
            "telegram_username": message.from_user.username,
        },
    )
    if created:
        bot.send_message(
            chat_id,
            "Hello, {user}\nNice to meet you".format(user=message.from_user.first_name),
        )
    else:
        bot.send_message(
            chat_id, "Welcome back, {user}!".format(user=message.from_user.first_name)
        )
    if current_chat.authorised == False and current_chat.connected_user == None:
        inline_action = types.InlineKeyboardMarkup()
        inline_singin_button = types.InlineKeyboardButton(
            "Sign in", callback_data="c_signin"
        )
        inline_login_button = types.InlineKeyboardButton(
            "Log in", callback_data="c_login"
        )
        inline_stayunauth_button = types.InlineKeyboardButton(
            "Stay anonimous 👻", callback_data="c_anonym"
        )
        inline_action.row(inline_login_button, inline_singin_button)
        inline_action.row(inline_stayunauth_button)
        bot.send_message(chat_id, "Choose the action", reply_markup=inline_action)


@bot.message_handler(commands=["cancel"], content_types=["text"])
def cmd_cancel_handler(message):
    chat_id = message.chat.id
    chat = Chat.get_chat(chat_id)
    responce_message = (
        "Last action canceled, use commands or interacive keyboard to start new action"
    )
    if chat.state in [
        el.value
        for el in [
            State.SIGNING_IN_FNAME,
            State.SIGNING_IN_LNAME,
            State.SIGNING_IN_PASS,
            State.SIGNING_IN_CONFIRM_PASS,
        ]
    ]:
        if chat.connected_user != None:
            chat.connected_user.delete()
            chat.connected_user = None
    chat.state = State.NO_ACTIONS.value
    bot.send_message(chat_id, responce_message)
    if chat.authorised:
        authorised.keyboard(chat)
    else:
        unauthorised.keyboard(chat)
    chat.save()


@bot.message_handler(
    func=lambda message: True,
    content_types=[
        "audio",
        "photo",
        "voice",
        "video",
        "document",
        "text",
        "location",
        "contact",
        "sticker",
    ],
)
def default_handler(message):
    return bot.reply_to(message, "I have no idea what is it...")


@bot.edited_message_handler(
    func=lambda message: True,
    content_types=[
        "audio",
        "photo",
        "voice",
        "video",
        "document",
        "text",
        "location",
        "contact",
        "sticker",
    ],
)
def default_editmessage_handler(message):
    return bot.reply_to(message, "I do not handle edited messages")


bot.message_handlers.reverse()
tmp_hnd = bot.message_handlers[0]
bot.message_handlers.remove(bot.message_handlers[0])
bot.message_handlers.append(tmp_hnd)
