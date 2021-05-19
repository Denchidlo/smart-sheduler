from datetime import datetime
from django.conf import settings
from .common_objects import *
from telebot import types


def button_group(chat):
    try:
        chat_id = chat.chat_id
        group = chat.connected_user.group
        markup = types.InlineKeyboardMarkup(row_width=1)
        group_info = types.InlineKeyboardButton(
            "Group info", callback_data=f"group={group.name}|cmd=info"
        )
        day = datetime.now().weekday() + 1
        group_schedule = types.InlineKeyboardButton(
            "Group schedule",
            callback_data=f"group={group.name}|day={day}|week={settings.CURRENT_WEEK}",
        )
        if group.grouplead.user.id == chat.connected_user.id:
            notify_all_button = types.InlineKeyboardButton(
                "Notify group", callback_data=f"group={group.name}|cmd=notify"
            )
            membership_requests = types.InlineKeyboardButton(
                "Requests",
                callback_data=f"group={group.name}|cmd=membership|page=0",
            )
        markup.add(group_info, group_schedule, notify_all_button, membership_requests)
        bot.send_message(chat_id, "Choose the action:", reply_markup=markup)
    except:
        pass


def button_request_membership(chat):
    chat_id = chat.chat_id
    chat.state = State.ON_GROUP_REQUEST_NAME.value
    bot.send_message(chat_id, "Set group name:")
    chat.save()


def request_group_input(chat, message_input):
    chat_id = chat.chat_id
    try:
        group = StudentGroup.objects.get(name=message_input)
        chat.connected_user.request_group = group
        group.save()
        chat.connected_user.save()
        bot.send_message(chat_id, "Request was sent!")
        chat.state = State.ON_ACTIONS.value
        chat.save()
    except:
        bot.send_message(chat_id, "Invalid group name!\n\nTry again:\nSet group name:")


def notify_group_input(chat, message_input):
    if (
        chat.connected_user != None
        and chat.connected_user.group != None
        and chat.connected_user.group.head != None
        and chat.connected_user.group.grouplead.user.id == chat.connected_user.id
    ):
        chat_list = chat.connected_user.get_chatlist(chat.connected_user.group)
        for chat_id in chat_list:
            bot.send_message(
                chat_id,
                f"Notification from {chat.connected_user.username}\n\n{message_input}",
            )
    bot.send_message(chat.id, "Success!")


@bot.callback_query_handler(
    func=lambda call: re.match(r"^group=\d{6}\|cmd=[a-z]{4,10}$")
)
def group_action_handler(call: types.CallbackQuery):
    message: types.types.Message = call.message
    chat = Chat.get_chat(message.chat.id)
    if chat.connected_user != None and chat.connected_user.group != None:
        preparsed_values = call.data.split("|")
        group_requested = preparsed_values[0].split("=")[1]
        if group_requested == chat.connected_user.group.name:
            cmd = preparsed_values[1].split("=")[1]
            group = chat.connected_user.group
            if cmd == "info":
                group_name = group.name
                group_course = group.course
                head_name = group.grouplead.user.first_name if group.grouplead.user != None else "None"
                bot.edit_message_text(
                    f"Group number:{group_name}\nCourse:{group_course}\nGroup lead name:{head_name}",
                    chat_id=chat.chat_id,
                    message_id=message.message_id,
                )
            elif group.head.id == chat.connected_user.id:
                if cmd == "notify":
                    bot.edit_message_text(
                        f"Print your message:",
                        chat_id=chat.chat_id,
                        message_id=message.message_id,
                    )
                    chat.state = State.ON_ACTION_NOTIFY.value
        else:
            bot.edit_message_text(
                f"Oops, you came to far...\n\nMaybe you use irrelevant link",
                chat_id=chat.chat_id,
                message_id=message.message_id,
            )
    else:
        bot.edit_message_text(
            text=f"Oops, you came to far...\n\nJoin any group firstly",
            chat_id=chat.chat_id,
            message_id=message.message_id,
        )


@bot.callback_query_handler(
    func=lambda call: re.fullmatch(r"group=\d{6}\|cmd=membership\|page=[0-9]$")
)
def group_requests_handler(call: types.CallbackQuery):
    message: types.types.Message = call.message
    chat = Chat.get_chat(message.chat.id)
    preparsed_values = call.data.split("|")
    page = int(preparsed_values[2].split("=")[1])
    if (
        chat.connected_user != None
        and chat.connected_user.group != None
        and chat.connected_user.group.grouplead.user != None
        and chat.connected_user.group.grouplead.user.id == chat.connected_user.id
    ):
        group = chat.connected_user.group
        reqs, size = group.get_requests(page)
        markup = types.InlineKeyboardMarkup(row_width=1)
        for el in reqs:
            user_link = types.InlineKeyboardButton(
                f"{el.uname}| {el.first_name} {el.last_name}",
                callback_data=f"group={group.name}|cmd=user_action|id={el.id}",
            )
            markup.row(user_link)
        next_page = page + 1 if (5 * (page + 1) < size) else page
        prev_page = page - 1 if page != 0 else page
        button_next = types.InlineKeyboardButton(
            "next", callback_data=f"group={group.name}|cmd=membership|page={next_page}"
        )
        button_prev = types.InlineKeyboardButton(
            "prev", callback_data=f"group={group.name}|cmd=membership|page={prev_page}"
        )
        button_cancel = types.InlineKeyboardButton(
            "❌", callback_data=f"group={group.name}|cmd=stop"
        )
        markup.row(button_prev, button_cancel, button_next)
        bot.edit_message_text(
            text=f"Requsts in {group.name}:",
            chat_id=chat.chat_id,
            message_id=message.message_id,
            reply_markup=markup,
        )
    else:
        bot.edit_message_text(
            text=f"U need to be group leader",
            chat_id=chat.chat_id,
            message_id=message.message_id
        )