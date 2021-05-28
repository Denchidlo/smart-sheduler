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



def default_unauthorised_handler(chat, message):
    bot.reply_to(message, "Oops, i don't know what to do with it!")
    return button_actions(chat)




def button_login(chat):
    chat_id = chat.chat_id
    bot.send_message(chat_id, "Enter username:", reply_markup=CANCEL_MARKUP)
    chat.state = State.LOGING_IN_UNAME.value
    chat.save()


def button_signin(chat):
    chat_id = chat.chat_id
    chat = Chat.objects.get(chat_id=chat_id)
    bot.send_message(chat_id, "Enter username:", reply_markup=CANCEL_MARKUP)
    chat.state = State.SIGNING_IN_UNAME.value
    chat.save()


def keyboard(chat, message=None):
    chat.save()
    bot.send_message(
        chat.chat_id,
        text="What do you want, stranger?",
        reply_markup=UNAUTHORISED_KB_MARKUP,
    )


def button_actions(chat):
    chat_id = chat.chat_id
    chat.state = State.ON_ACTIONS.value
    bot.send_message(chat_id, "Actions:", reply_markup=UNAUTHORISED_ACTIONS_MARKUP)
    chat.save()


@bot.callback_query_handler(func=lambda call: call.data == "c_anonym")
def anonym_handler(call):
    logging.debug(f"Registered callback with callback data :{call.data}")
    message: types.types.Message = call.message
    chat = Chat.get_chat(message.chat.id)
    chat.state = State.NO_ACTIONS.value
    keyboard(chat)
    chat.save()


def button_back_to_keyboard(chat):
    chat.state = State.NO_ACTIONS.value
    chat.save()
    keyboard(chat)

unauthorised_action_handler_map = {
    State.NO_ACTIONS.value: {
        "Actions 📋": button_actions,
        "Login": button_login,
        "Sign in": button_signin,
        "default": keyboard
    },
    State.ON_ACTIONS.value: {
        "Get schedule": button_get_schedule,
        "Back to keyboard": button_back_to_keyboard,
        "default": default_unauthorised_handler
    }
}

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
    if state == State.ON_ACTION_SCHEDULE_GROUP_ENTER.value:
        return schedule_group_input(chat, request)
    else:
        state_handler = unauthorised_action_handler_map[state]
        if request in state_handler.keys():
            if request != "default":
                return state_handler[request](chat)
            else:
                return state_handler[request](chat, message)
        return state_handler['default'](chat, message)