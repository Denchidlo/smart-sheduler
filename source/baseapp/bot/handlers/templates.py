from telebot import types


# Common markup templates
CANCEL_MARKUP = types.ReplyKeyboardMarkup(row_width=1)
CANCEL_MARKUP.add(types.KeyboardButton("/cancel"))


AUTHORISED_KB_MARKUP = types.ReplyKeyboardMarkup(
    one_time_keyboard=True, row_width=1)
actions_button = types.KeyboardButton("Actions 📋")
logout_button = types.KeyboardButton("Logout 🚶‍♂️")
AUTHORISED_KB_MARKUP.add(actions_button, logout_button)


UNAUTHORISED_KB_MARKUP = types.ReplyKeyboardMarkup(
    one_time_keyboard=True, row_width=1)
actions_button = types.KeyboardButton("Actions 📋")
login_button = types.KeyboardButton("Login")
signin_button = types.KeyboardButton("Sign in")
UNAUTHORISED_KB_MARKUP.add(actions_button)
UNAUTHORISED_KB_MARKUP.row(login_button, signin_button)


UNAUTHORISED_ACTIONS_MARKUP = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
get_schedule = types.KeyboardButton("Get schedule")
back_to_action = types.KeyboardButton("Back to keyboard")
UNAUTHORISED_ACTIONS_MARKUP.add(get_schedule)
UNAUTHORISED_ACTIONS_MARKUP.add(back_to_action)

