from django.contrib.auth.models import Group
from .common_objects import *
from telebot import types


def button_get_schedule(chat):
    chat_id = chat.chat_id
    chat.state = State.ON_ACTION_SCHEDULE_GROUP_ENTER.value
    bot.send_message(chat_id, "Set group number:")
    chat.save()


def schedule_group_input(chat, message_input):
    chat_id = chat.chat_id
    try:
        group = StudentGroup.objects.get(name=message_input)
        callback_template = f"group={message_input}|day="
        markup = types.InlineKeyboardMarkup(row_width=1)
        mon_button = types.InlineKeyboardButton(
            "Понедельник", callback_data=callback_template + "1"
        )
        tue_button = types.InlineKeyboardButton(
            "Вторник", callback_data=callback_template + "2"
        )
        wed_button = types.InlineKeyboardButton(
            "Среда", callback_data=callback_template + "3"
        )
        fou_button = types.InlineKeyboardButton(
            "Четверг", callback_data=callback_template + "4"
        )
        fri_button = types.InlineKeyboardButton(
            "Пятница", callback_data=callback_template + "5"
        )
        sat_button = types.InlineKeyboardButton(
            "Суббота", callback_data=callback_template + "6"
        )
        markup.add(
            mon_button, tue_button, wed_button, fou_button, fri_button, sat_button
        )
        chat.state = State.NO_ACTIONS.value
        chat.save()
        bot.send_message(chat_id, "Select day:", reply_markup=markup)
    except:
        bot.send_message(chat_id, "Invalid group name!\n\nTry again:")


@bot.callback_query_handler(
    func=lambda call: re.fullmatch(r"^group=\d{6}\|day=[1-6]{1}$", call.data)
)
def weekday_input_handler(call: types.CallbackQuery):
    message: types.types.Message = call.message
    callback_template = f"{call.data}|week="
    markup = types.InlineKeyboardMarkup(row_width=2)
    button_1 = types.InlineKeyboardButton(
        "1", callback_data=callback_template + "1"
    )
    button_2 = types.InlineKeyboardButton(
        "2", callback_data=callback_template + "2"
    )
    button_3 = types.InlineKeyboardButton(
        "3", callback_data=callback_template + "3"
    )
    button_4 = types.InlineKeyboardButton(
        "4", callback_data=callback_template + "4"
    )
    markup.row(button_1, button_2)
    markup.row(button_3, button_4)
    bot.edit_message_text(
        "Choose week:",
        chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup
    )


@bot.callback_query_handler(
    func=lambda call: re.fullmatch(
        r"^group=\d{6}\|day=[1-6]{1}\|week=[1-4]{1}$", call.data
    )
)
def week_input_handler(call: types.CallbackQuery):
    message: types.types.Message = call.message
    chat = Chat.get_chat(message.chat.id)
    preparsed_values = call.data.split("|")
    group = preparsed_values[0].split("=")[1]
    day = int(preparsed_values[1].split("=")[1])
    week = int(preparsed_values[2].split("=")[1])
    group = StudentGroup.objects.get(name=group)
    schedule = group.get_schedule(day=day, week=week)
    schedule_markup = types.InlineKeyboardMarkup(row_width=2)
    for lesson in schedule:
        lesson_button = types.InlineKeyboardButton(
            lesson.subject,
            callback_data=f"lesson={lesson.id}|schedule=({call.data})",
        )
        schedule_markup.add(lesson_button)
    next_button = types.InlineKeyboardButton(
        "➡️", next_schedule_string(group, day, week)
    )
    prev_button = types.InlineKeyboardButton(
        "⬅️", prev_schedule_string(group, day, week)
    )
    # schedule_markup.add(prev_button, next_button)
    responce_message = f"Group:{group.name}\nDay:{int_to_weekday(day).value[1]}\nWeek:{week}"
    bot.edit_message_text(
        text=responce_message,
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=schedule_markup,
    )

@bot.callback_query_handler(
    func=lambda call: re.fullmatch(
        r"^lesson=[0-9]{1,10}\|schedule=\(group=[0-9]{6}\|day=[1-6]{1}\|week=[1-4]{1}\)$",
        call.data,
    )
)
def lesson_info(call):
    message: types.types.Message = call.message
    preparsed_values = call.data.split("|")
    lesson_id = int(preparsed_values[0].split("=")[1])
    call_data = call.data.split("(")[1].split(")")[0]
    lesson = Lesson.objects.get(id=lesson_id)
    responce_message = f"Subject:{lesson.subject}\nAuditory:{lesson.auditory[1:-1]}\nDuration:{lesson.lesson_time}\nEmployee: {lesson.employee.fio}"
    markup = types.InlineKeyboardMarkup()
    button_back = types.InlineKeyboardButton(
        "Back", callback_data=call_data)
    markup.add(button_back)
    bot.edit_message_text(
        responce_message,
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=markup,
    )
