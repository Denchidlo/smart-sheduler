from .common_objects import *
from .authorised import keyboard


@bot.callback_query_handler(lambda call: call.data == "c_signin")
def button_signin(call: types.CallbackQuery):
    logging.debug(f"Registered callback with callback data :{call.data}")
    callback_message = call.message
    try:
        chat_id = callback_message.chat.id
        chat = Chat.objects.get(chat_id=chat_id)
        if not chat.authorised:
            bot.send_message(chat_id, "Enter username:", reply_markup=CANCEL_MARKUP)
            chat.state = State.SIGNING_IN_UNAME.value
            chat.save()
        else:
            bot.send_message(
                chat_id, "You need to logout first", reply_markup=CANCEL_MARKUP
            )
    except Exception:
        bot.send_message(
            callback_message.chat.id,
            "Something went wrong\nTry again",
            reply_markup=CANCEL_MARKUP,
        )


@bot.message_handler(
    func=lambda message: onstate(
        message.chat.id,
        [State.SIGNING_IN_UNAME, State.SIGNING_IN_FNAME, State.SIGNING_IN_LNAME],
    )
)
def signin_data_input(message):
    message_input = message.text
    chat_id = message.chat.id
    chat = Chat.objects.get(chat_id=chat_id)
    responce_message = ""
    if chat.state == State.SIGNING_IN_UNAME.value:
        if validate_username(message_input):
            user, created = ScheduleUser.objects.get_or_create(
                username=message_input,
                defaults={
                    "first_name": "Fname template",
                    "last_name": "Lname template",
                },
            )
            if not created:
                responce_message = (
                    "Username alreasy exsist!\n\nTry to make unique username:"
                )
            else:
                responce_message = "Set first name"
                chat.connected_user = user
                chat.state = State.SIGNING_IN_FNAME.value
        else:
            responce_message = (
                "Username shuold contain from 5 to 30 letters/digits\n\nTry again:"
            )
    elif validate_name(message_input):
        if chat.state == State.SIGNING_IN_FNAME.value:
            responce_message = "Set last name"
            chat.connected_user.first_name = message_input
            chat.state = State.SIGNING_IN_LNAME.value
        else:
            responce_message = "Set password"
            chat.connected_user.last_name = message_input
            chat.state = State.SIGNING_IN_PASS.value
        chat.connected_user.save()
    else:
        responce_message = "Name and lastname should be from 5 to 30 and consist of letters\n\nTry again:"
    bot.send_message(chat_id, responce_message, reply_markup=CANCEL_MARKUP)
    chat.save()


@bot.message_handler(
    func=lambda message: onstate(
        message.chat.id, [State.SIGNING_IN_PASS, State.SIGNING_IN_CONFIRM_PASS]
    )
)
def signin_password_input(message):
    message_input = message.text
    chat_id = message.chat.id
    chat = Chat.objects.get(chat_id=chat_id)
    responce_message = ""
    if validate_pass(message_input):
        if chat.state == State.SIGNING_IN_PASS.value:
            chat.connected_user.set_password(message_input)
            chat.connected_user.save()
            responce_message = "Confirm password"
            chat.state = State.SIGNING_IN_CONFIRM_PASS.value
        elif (
            chat.state == State.SIGNING_IN_CONFIRM_PASS.value
            and chat.connected_user.check_password(message_input)
        ):
            chat.authorised = True
            responce_message = "Success ✔️"
            chat.state = State.NO_ACTIONS.value
            keyboard(chat)
        else:
            responce_message = "Wrong password!\n\nTry again:"
    else:
        responce_message = """Conditions for a valid password are: 🔒

    Should have at least one number.
    Should have at least one uppercase and one lowercase character.
    Should have at least one special symbol (In most case just add one #).
    Should be between 6 to 20 characters long.
    
    Try again:"""
    chat.save()
    bot.send_message(
        chat_id,
        responce_message,
        reply_markup=CANCEL_MARKUP if responce_message != "Success ✔️" else None,
    )
