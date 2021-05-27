from enum import unique
from .common_objects import *
from telebot import types

account_handled_states = [
    State.ON_ACCOUNT_USERNAME_INPUT,
    State.ON_ACCOUNT_FULLNAME_INPUT,
    State.ON_ACCOUNT_PASSCHG_CONFIRM,
    State.ON_ACCOUNT_PASSCHG_INPUT,
    State.ON_ACCOUNT_DELETE,
]


@bot.message_handler(
    content_types=["text"],
    func=lambda message: authorized(message.chat.id)
    and onstate(message.chat.id, account_handled_states),
)
def group_actions_handler(message: types.Message):
    result = None
    chat_id = message.chat.id
    chat = Chat.get_chat(chat_id)
    state = chat.state
    request = message.text
    if state == State.ON_ACCOUNT_USERNAME_INPUT.value:
        result = username_change_input(chat, request)
    elif state == State.ON_ACCOUNT_FULLNAME_INPUT.value:
        result = fullname_change_input(chat, request)
    elif state == State.ON_ACCOUNT_PASSCHG_CONFIRM.value:
        result = password_change_confirm(chat, request)
    elif state == State.ON_ACCOUNT_PASSCHG_INPUT.value:
        result = password_change_input(chat, request)
    elif state == State.ON_ACCOUNT_DELETE.value:
        result = delete_user_input(chat, request)
    else:
        result = bot.reply_to(message, "Oops, i don't know what to do with it!")
    return result


def username_change_input(chat, message_input):
    chat_id = chat.chat_id
    try:
        ScheduleUser.objects.get(username=message_input)
        unique = True
    except:
        unique = False
    if validate_username(message_input) and unique:
        chat.connected_user.username = message_input
        chat.connected_user.save()
        chat.state = State.ON_ACCOUNT.value
        chat.save()
        return bot.send_message(
            chat_id, "Username changed", reply_markup=AUTHORISED_ACCOUNT_MARKUP
        )
    else:
        return bot.send_message(
            chat_id,
            "Username shuold contain from 5 to 30 letters/digits\nMaybe it's not unique\nTry again:",
            reply_markup=CANCEL_MARKUP,
        )


def fullname_change_input(chat, message_input):
    names = message_input.split(" ")
    if len(names) == 2 and validate_name(names[0]) and validate_name(names[1]):
        chat.connected_user.first_name = names[0]
        chat.connected_user.last_name = names[1]
        chat.connected_user.save()
        chat.state = State.ON_ACCOUNT.value
        chat.save()
        return bot.send_message(
            chat.chat_id, "Full name changed", reply_markup=AUTHORISED_ACCOUNT_MARKUP
        )
    else:
        return bot.send_message(
            chat.chat_id,
            "First name and last name should be from 5 to 30 and consist of letters and separated with whitespace\nTry again:",
            reply_markup=CANCEL_MARKUP,
        )


def password_change_confirm(chat, message_input):
    if chat.connected_user.check_password(message_input):
        chat.state = State.ON_ACCOUNT_PASSCHG_INPUT.value
        chat.save()
        return bot.send_message(
            chat.chat_id, "Set new password:", reply_markup=CANCEL_MARKUP
        )
    else:
        return bot.send_message(
            chat.chat_id, "Wrong password\nTry again:", reply_markup=CANCEL_MARKUP
        )


def password_change_input(chat, message_input):
    if validate_pass(message_input):
        chat.connected_user.set_password(message_input)
        chat.connected_user.save()
        chat.state = State.ON_ACCOUNT.value
        chat.save()
        return bot.send_message(
            chat.chat_id, "Password changed", reply_markup=AUTHORISED_ACCOUNT_MARKUP
        )
    else:
        return bot.send_message(
            chat.chat_id, PASSWORD_VALIDATION_MESSAGE, reply_markup=CANCEL_MARKUP
        )


def delete_user_input(chat, message_input):
    if message_input == "Agree":
        user = chat.connected_user
        chat.connected_user = None
        chat.authorised = False
        chat.state = State.NO_ACTIONS.value
        chat.save()
        if user.group.grouplead.user.id == user.id:
            user.group.grouplead.user = None
            user.group.grouplead.save()
            user.group.save()
        user.save()
        user.delete()
        return bot.send_message(
            chat.chat_id,
            "User deleted, you were logged out",
            reply_markup=UNAUTHORISED_KB_MARKUP,
        )
    elif message_input == "Abort":
        chat.state = State.ON_ACCOUNT.value
        chat.save()
        return bot.send_message(
            chat.chat_id, "Deletion aborted", reply_markup=AUTHORISED_ACCOUNT_MARKUP
        )
    else:
        return bot.send_message(
            chat.chat_id, "Invalid operation", reply_markup=ACCOUNT_DELETE_MARKUP
        )


def edit_username_button(chat):
    chat_id = chat.chat_id
    chat.state = State.ON_ACCOUNT_USERNAME_INPUT.value
    chat.save()
    return bot.send_message(chat_id, "Set new username:", reply_markup=CANCEL_MARKUP)


def edit_full_name_button(chat):
    chat_id = chat.chat_id
    chat.state = State.ON_ACCOUNT_FULLNAME_INPUT.value
    chat.save()
    return bot.send_message(
        chat_id,
        "Full name format:\n<first name> <last name>\nSet new full name:",
        reply_markup=CANCEL_MARKUP,
    )


def edit_password_button(chat):
    chat_id = chat.chat_id
    chat.state = State.ON_ACCOUNT_PASSCHG_CONFIRM.value
    chat.save()
    return bot.send_message(
        chat_id, "Confirm your previous password:", reply_markup=CANCEL_MARKUP
    )


def delete_user_button(chat):
    chat_id = chat.chat_id
    chat.state = State.ON_ACCOUNT_DELETE.value
    chat.save()
    return bot.send_message(
        chat_id, "Are you sure?", reply_markup=ACCOUNT_DELETE_MARKUP
    )
