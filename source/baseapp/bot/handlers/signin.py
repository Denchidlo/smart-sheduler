from django.db import models
from .common_objects import *

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
            chat.state = State.SIGNING_IN_FNAME.value
            chat.connected_user = ScheduleUser.objects.create(message_input, "template", "template")
            bot.send_message(chat_id, "Enter first name:")
        else:
            chat.state = State.NO_ACTIONS.value
            bot.send_message(chat_id, "Username should contain from 5 to 30 digits/characters!")
        chat.save()

@bot.message_handler(content_types=['text'], func=lambda message: onstate(message.chat.id, State.SIGNING_IN_FNAME))
def signin_username_input(message):
    message_input = message.text
    chat_id = message.chat.id
    chat = Chat.objects.get(chat_id=chat_id)
    try:
        _ = ScheduleUser.objects.get(username=message_input)
        bot.send_message(chat_id, 'Username is used by somebody else!')
        chat.state = State.NO_ACTIONS.value
    except Exception:
        if validate_name(message_input):
            chat.state = State.SIGNING_IN_LNAME.value
            chat.connected_user = ScheduleUser.objects.create(message_input, "template", "template")
            chat.connected_user.first_name = message_input
            chat.connected_user.save()
            bot.send_message(chat_id, "Enter first name:")
        else:
            chat.state = State.NO_ACTIONS.value
            bot.send_message(chat_id, "First name should contain from 5 to 30 characters!")
        chat.save()

@bot.message_handler(content_types=['text'], func=lambda message: onstate(message.chat.id, State.SIGNING_IN_FNAME))
def signin_username_input(message):
    message_input = message.text
    chat_id = message.chat.id
    chat = Chat.objects.get(chat_id=chat_id)
    try:
        _ = ScheduleUser.objects.get(username=message_input)
        bot.send_message(chat_id, 'Username is used by somebody else!')
        chat.state = State.NO_ACTIONS.value
    except Exception:
        if validate_name(message_input):
            chat.state = State.SIGNING_IN_PASS.value
            chat.connected_user = ScheduleUser.objects.create(message_input, "template", "template")
            chat.connected_user.first_name = message_input
            chat.connected_user.save()
            bot.send_message(chat_id, "Enter first name:")
        else:
            chat.state = State.NO_ACTIONS.value
            bot.send_message(chat_id, "First name should contain from 5 to 30 characters!")
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