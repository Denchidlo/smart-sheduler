from .common_objects import *
from telebot import types

handled_states = [
    State.NO_ACTIONS,
    State.ON_ACTIONS,
]


@bot.message_handler(
    content_types=["text"],
    func=lambda message: authorized(message.chat.id)
    and onstate(message.chat.id, handled_states),
)
def authorised_actions_handler(message: types.Message):
    chat_id = message.chat.id
    chat = Chat.get_chat(chat_id)
    state = chat.state
    request = message.text
    if state == State.NO_ACTIONS.value:
        if request == "Actions 📋":
            button_actions(chat)
            return
        if request == "Logout 🚶‍♂️":
            button_logout(chat)
            return
        keyboard(chat)
        return
    elif state == State.ON_ACTIONS:
        if request == "Get schedule":
            pass
        elif request == "Find employee":
            pass
        elif request == "Find employee":
            pass
        elif request == "Find employee":
            pass
        button_actions(chat)


def keyboard(chat):
    user = chat.connected_user
    if user != None:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
        actions_button = types.KeyboardButton("Actions 📋")
        logout_button = types.KeyboardButton("Logout 🚶‍♂️")
        markup.add(actions_button, logout_button)
        bot.send_message(
            chat.chat_id,
            text="What do you want, {username}".format(username=user.first_name),
            reply_markup=markup,
        )
    else:
        raise ValueError("Unauthorised access of authorised.keyboard")


def button_logout(chat):
    chat_id = chat.chat_id
    chat.state = State.NO_ACTIONS.value
    chat.connected_user = None
    chat.authorised = False
    bot.send_message(
        chat_id, "You successfuly logged out\nPrint command /start to use bot"
    )
    chat.save()


def button_actions(chat):
    chat_id = chat.chat_id
    chat.state = State.ON_ACTIONS.value
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    get_schedule = types.KeyboardButton("Get schedule")
    get_employee = types.KeyboardButton("Find employee")
    if group_member(chat_id):
        group_actions = types.KeyboardButton("Group")
    else:
        group_actions = types.KeyboardButton("Requet group membership")
    back_to_action = types.KeyboardButton("Back to keyboard")
    markup.add(get_employee, get_schedule)
    markup.add(group_actions, back_to_action)
    bot.send_message(chat_id, "Actions:", reply_markup=markup)
    chat.save()


def button_back_to_keyboard(chat):
    chat.state = State.NO_ACTIONS.value
    keyboard(chat)
