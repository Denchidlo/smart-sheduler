from .schedule import button_get_schedule, schedule_group_input
from .login import button_login
from .signin import button_signin
from .authorised import button_get_schedule
from .common_objects import *
from telebot import types


handled_states = [
    State.NO_ACTIONS,
    State.ON_ACTIONS,
    State.ON_ACTION_SCHEDULE_GROUP_ENTER,
]


@bot.message_handler(
    content_types=["text"],
    func=lambda message: not authorized(message.chat.id)
    and onstate(message.chat.id, handled_states),
)
def unauthorised_actions_handler(message: types.Message):
    chat_id = message.chat.id
    chat = Chat.get_chat(chat_id)
    state = chat.state
    request = message.text
    if state == State.NO_ACTIONS.value:
        if request == "Actions 📋":
            button_actions(chat)
            return
        if request == "Login":
            button_login(chat)
            return
        if request == "Sign in":
            button_signin(chat)
            return
        keyboard(chat)
        return
    elif state == State.ON_ACTIONS.value:
        if request == "Get schedule":
            button_get_schedule(chat)
            return
        elif request == "Back to keyboard":
            button_back_to_keyboard(chat)
            return
        button_actions(chat)
        bot.reply_to(message, "Oops, i don't know what to do with it!")
        return
    elif state == State.ON_ACTION_SCHEDULE_GROUP_ENTER.value:
        schedule_group_input(chat, request)
        return
    else:
        keyboard(chat)
        bot.reply_to(message, "Oops, i don't know what to do with it!")


def button_login(chat):
    chat_id = chat.chat_id
    if not chat.authorised:
        bot.send_message(chat_id, "Enter username:")
        chat.state = State.LOGING_IN_UNAME.value
        chat.save()
    else:
        bot.send_message(chat_id, "You need to logout first")


def button_signin(chat):
    chat_id = chat.chat_id
    chat = Chat.objects.get(chat_id=chat_id)
    if not chat.authorised:
        bot.send_message(chat_id, "Enter username:")
        chat.state = State.SIGNING_IN_UNAME.value
        chat.save()
    else:
        bot.send_message(chat_id, "You need to logout first")


def keyboard(chat):
    user = chat.connected_user
    if user == None:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
        actions_button = types.KeyboardButton("Actions 📋")
        login_button = types.KeyboardButton("Login")
        signin_button = types.KeyboardButton("Sign in")
        markup.add(actions_button)
        markup.row(login_button, signin_button)
        bot.send_message(
            chat.chat_id,
            text="What do you want, stranger?",
            reply_markup=markup,
        )
    else:
        raise ValueError("Unauthorised access of authorised.keyboard")


def button_actions(chat):
    chat_id = chat.chat_id
    chat.state = State.ON_ACTIONS.value
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    get_schedule = types.KeyboardButton("Get schedule")
    back_to_action = types.KeyboardButton("Back to keyboard")
    markup.add(get_schedule)
    markup.add(back_to_action)
    bot.send_message(chat_id, "Actions:", reply_markup=markup)
    chat.save()


@bot.callback_query_handler(
    func=lambda call: call.data == "c_anonym"
)
def anonym_handler(call):
    message: types.types.Message = call.message
    chat = Chat.get_chat(message.chat.id)
    chat.state = State.NO_ACTIONS.value
    keyboard(chat)
    chat.save()


def button_back_to_keyboard(chat):
    chat.state = State.NO_ACTIONS.value
    chat.save()
    keyboard(chat)
