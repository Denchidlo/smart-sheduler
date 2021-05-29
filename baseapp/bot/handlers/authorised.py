from .schedule import button_get_schedule
from .groups import button_group, button_request_membership
from .account import (
    edit_full_name_button,
    edit_password_button,
    edit_username_button,
    delete_user_button,
)
from .common_objects import *
from telebot import types

authorised_handled_states = [
    State.NO_ACTIONS,
    State.ON_ACTIONS,
    State.ON_ACCOUNT,
]


def on_actions_default(chat, message):
    button_actions(chat)
    return bot.reply_to(message, "Oops, i don't know what to do with it!")


def on_account_default(chat, message):
    button_account(chat)
    return bot.reply_to(message, "Oops, i don't know what to do with it!")


def keyboard(chat, message=None):
    user = chat.connected_user
    return bot.send_message(
        chat.chat_id,
        text="What do you want, {username}".format(username=user.first_name),
        reply_markup=AUTHORISED_KB_MARKUP,
    )


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


def button_account(chat):
    chat_id = chat.chat_id
    chat.state = State.ON_ACCOUNT.value
    user = chat.connected_user
    chat.save()
    return bot.send_message(
        chat_id,
        f"Username: {user.username}\nFull name: {user.first_name} {user.last_name}\nAccount settings:",
        reply_markup=AUTHORISED_ACCOUNT_MARKUP,
    )


def button_back_to_keyboard(chat):
    chat.state = State.NO_ACTIONS.value
    chat.save()
    return keyboard(chat)


authorised_action_handler_map = {
    State.NO_ACTIONS.value: {
        "Actions 📋": button_actions,
        "Account 📝": button_account,
        "Logout 🚶‍♂️": button_logout,
        "default": keyboard,
    },
    State.ON_ACTIONS.value: {
        "Get schedule": button_get_schedule,
        "Group": button_group,
        "Request group membership": button_request_membership,
        "Back to keyboard": button_back_to_keyboard,
        "default": on_actions_default,
    },
    State.ON_ACCOUNT.value: {
        "Edit username": edit_username_button,
        "Edit first and last name": edit_full_name_button,
        "Edit password": edit_password_button,
        "Delete user": delete_user_button,
        "Back to keyboard": button_back_to_keyboard,
        "default": on_account_default,
    },
}


@bot.message_handler(
    content_types=["text"],
    func=lambda message: authorized(message.chat.id)
    and onstate(message.chat.id, authorised_handled_states),
)
def authorised_actions_handler(message: types.Message):
    chat_id = message.chat.id
    chat = Chat.get_chat(chat_id)
    state = chat.state
    request = message.text
    state_handler = authorised_action_handler_map[state]
    if request in state_handler.keys():
        if request != "default":
            return state_handler[request](chat)
        else:
            return state_handler[request](chat, message)
    return state_handler["default"](chat, message)
