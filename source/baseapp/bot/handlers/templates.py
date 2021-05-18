from telebot import types

base_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
actions_button = types.KeyboardButton("Actions 📋")
logout_button = types.KeyboardButton("Logout 🚶‍♂️")
base_markup.add(actions_button, logout_button)
