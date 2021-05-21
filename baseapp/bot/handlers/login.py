from .common_objects import *
from .authorised import keyboard


@bot.callback_query_handler(lambda call: call.data == "c_login")
def button_login(call: types.CallbackQuery):
    logging.debug(f"Registered callback with callback data :{call.data}")
    callback_message = call.message
    try:
        chat_id = callback_message.chat.id
        chat = Chat.objects.get(chat_id=chat_id)
        if not chat.authorised:
            bot.send_message(chat_id, "Enter username:", reply_markup=CANCEL_MARKUP)
            chat.state = State.LOGING_IN_UNAME.value
            chat.save()
        else:
            bot.send_message(
                chat_id, "You need to logout first", reply_markup=CANCEL_MARKUP
            )
    except Exception as ex:
        bot.send_message(
            callback_message.chat.id,
            "Something went wrong\nTry again",
            reply_markup=CANCEL_MARKUP,
        )


@bot.message_handler(
    content_types=["text"],
    func=lambda message: onstate(message.chat.id, [State.LOGING_IN_UNAME]),
)
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
    bot.send_message(chat_id, "Enter password:", reply_markup=CANCEL_MARKUP)


@bot.message_handler(
    content_types=["text"],
    func=lambda message: onstate(message.chat.id, [State.LOGING_IN_PASS]),
)
def login_password_input(message):
    message_input = message.text
    chat_id = message.chat.id
    chat = Chat.objects.get(chat_id=chat_id)
    if (
        chat.connected_user != None
        and chat.connected_user.check_password(message_input) == True
    ):
        chat.authorised = True
        bot.send_message(chat_id, "Success!")
        chat.state = State.NO_ACTIONS.value
        keyboard(chat)
    else:
        chat.connected_user = None
        bot.send_message(
            chat_id, "Login failed!\nIvalid username or password\nTry again:"
        )
        bot.send_message(chat_id, "Enter username:", reply_markup=CANCEL_MARKUP)
        chat.state = State.LOGING_IN_UNAME.value
    chat.save()
