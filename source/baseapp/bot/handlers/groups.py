from datetime import datetime
from django.conf import settings
from .common_objects import *
from telebot import types

def button_group(chat):
    try:
        chat_id = chat.chat_id
        group = chat.connected_user.group
        markup = types.InlineKeyboardMarkup(row_width=1)
        group_info = types.InlineKeyboardButton("Group info", callback_data=f"group={group.name}|cmd=info")
        day = datetime.now().weekday() + 1
        group_schedule = types.InlineKeyboardButton("Group schedule", callback_data=f"group={group.name}|day={day}|week={settings.CURRENT_WEEK}")
        if group.head.id == chat.connected_user.id:
            notify_all_button = types.InlineKeyboardButton("Notify group", callback_data=f"group={group.name}|cmd=notify")
            membership_requests = types.InlineKeyboardButton("Group schedule", callback_data=f"group={group.name}|cmd=membership")
        markup.add(group_info, group_schedule, notify_all_button, membership_requests)
        bot.send_message(chat_id, "Choose the action:", reply_markup=markup)
    except:
        pass

def button_request_membership(chat):
    pass