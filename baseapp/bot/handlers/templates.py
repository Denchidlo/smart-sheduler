from telebot import types

PASSWORD_VALIDATION_MESSAGE = """Conditions for a valid password are: 🔒

    Should have at least one number.
    Should have at least one uppercase and one lowercase character.
    Should have at least one special symbol (In most case just add one #).
    Should be between 6 to 20 characters long.
    
    Try again:"""

# Common markup templates
CANCEL_MARKUP = types.ReplyKeyboardMarkup(row_width=1)
CANCEL_MARKUP.add(types.KeyboardButton("/cancel"))


AUTHORISED_KB_MARKUP = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
_actions_button = types.KeyboardButton("Actions 📋")
_account_button = types.KeyboardButton("Account 📝")
_logout_button = types.KeyboardButton("Logout 🚶‍♂️")
AUTHORISED_KB_MARKUP.add(_actions_button, _account_button, _logout_button)

AUTHORISED_ACCOUNT_MARKUP = types.ReplyKeyboardMarkup(
    one_time_keyboard=True, row_width=1
)
_edit_username_button = types.KeyboardButton("Edit username")
_edit_full_name_button = types.KeyboardButton("Edit first and last name")
_edit_password_button = types.KeyboardButton("Edit password")
_delete_user_button = types.KeyboardButton("Delete user")
_back_to_action = types.KeyboardButton("Back to keyboard")
AUTHORISED_ACCOUNT_MARKUP.row(_edit_username_button)
AUTHORISED_ACCOUNT_MARKUP.row(_edit_full_name_button)
AUTHORISED_ACCOUNT_MARKUP.row(_edit_password_button, _delete_user_button)
AUTHORISED_ACCOUNT_MARKUP.row(_back_to_action)

UNAUTHORISED_KB_MARKUP = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
_actions_button = types.KeyboardButton("Actions 📋")
_login_button = types.KeyboardButton("Login")
_signin_button = types.KeyboardButton("Sign in")
UNAUTHORISED_KB_MARKUP.add(_actions_button)
UNAUTHORISED_KB_MARKUP.row(_login_button, _signin_button)


UNAUTHORISED_ACTIONS_MARKUP = types.ReplyKeyboardMarkup(
    row_width=1, one_time_keyboard=True
)
_get_schedule = types.KeyboardButton("Get schedule")
UNAUTHORISED_ACTIONS_MARKUP.add(_get_schedule)
UNAUTHORISED_ACTIONS_MARKUP.add(_back_to_action)

ACCOUNT_DELETE_MARKUP = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
_agree_button = types.KeyboardButton("Agree")
_abort_button = types.KeyboardButton("Abort")
ACCOUNT_DELETE_MARKUP.add(_agree_button, _abort_button)
