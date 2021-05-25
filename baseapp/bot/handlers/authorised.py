from .schedule import button_get_schedule, schedule_group_input
from .groups import (
    button_group,
    button_request_membership,
    notify_group_input,
    request_group_input,
)
from .common_objects import *
from telebot import types

handled_states = [
    State.NO_ACTIONS,
    State.ON_ACTIONS,
    State.ON_GROUP_REQUEST_NAME,
    State.ON_ACTION_SCHEDULE_GROUP_ENTER,
    State.ON_ACTION_NOTIFY,
]


@bot.message_handler(
    content_types=["text"],
    func=lambda message: authorized(message.chat.id)
    and onstate(message.chat.id, handled_states),
)
def authorised_actions_handler(message: types.Message):
    result = None
    chat_id = message.chat.id
    chat = Chat.get_chat(chat_id)
    state = chat.state
    request = message.text
    if state == State.NO_ACTIONS.value:
        if request == "Actions 📋":
            result = button_actions(chat)
        elif request == "Logout 🚶‍♂️":
            result = button_logout(chat)
        else:
            result = keyboard(chat)
    elif state == State.ON_ACTIONS.value:
        if request == "Get schedule":
            result = button_get_schedule(chat)
        elif request == "Group":
            result = button_group(chat)
        elif request == "Request group membership":
            button_request_membership(chat)
        elif request == "Back to keyboard":
            result = button_back_to_keyboard(chat)
        else:
            button_actions(chat)
            result = bot.reply_to(message, "Oops, i don't know what to do with it!")
    elif state == State.ON_ACTION_SCHEDULE_GROUP_ENTER.value:
        result = schedule_group_input(chat, request)
    elif state == State.ON_ACTION_NOTIFY.value:
        result = notify_group_input(chat, request)
    elif state == State.ON_GROUP_REQUEST_NAME.value:
        result = request_group_input(chat, request)
    else:
        result = bot.reply_to(message, "Oops, i don't know what to do with it!")
    return result


def keyboard(chat):
    user = chat.connected_user
    if user != None:
        return bot.send_message(
            chat.chat_id,
            text="What do you want, {username}".format(username=user.first_name),
            reply_markup=AUTHORISED_KB_MARKUP,
        )
    else:
        raise ValueError("Unauthorised access of authorised.keyboard")


def button_logout(chat):
    chat_id = chat.chat_id
    chat.state = State.NO_ACTIONS.value
    chat.connected_user = None
    chat.authorised = False
    chat.save()
    return bot.send_message(
        chat_id, "You successfuly logged out\nPrint command /start to use bot"
    )


def button_actions(chat):
    chat_id = chat.chat_id
    chat.state = State.ON_ACTIONS.value
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    get_schedule = types.KeyboardButton("Get schedule")
    if chat.connected_user.is_member == True and chat.connected_user.group != None:
        group_actions = types.KeyboardButton("Group")
    else:
        group_actions = types.KeyboardButton("Request group membership")
    back_to_action = types.KeyboardButton("Back to keyboard")
    markup.add(get_schedule)
    markup.add(group_actions, back_to_action)
    chat.save()
    return bot.send_message(chat_id, "Actions:", reply_markup=markup)


def button_back_to_keyboard(chat):
    chat.state = State.NO_ACTIONS.value
    chat.save()
    return keyboard(chat)
