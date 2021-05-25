import pytest
from telebot import types, TeleBot
from .models import *
from .views import cmd_start_handler
from .services.bot_init import bot


def fetch_handler(name):
    el = next(
        filter(lambda el: el["function"].__name__ == name, bot.message_handlers))
    return el


@pytest.fixture
def chat():
    return types.Chat(112, 'private')


@pytest.fixture
def message_start():
    message = types.Message(1, None, None, chat, "text", {}, None)
    message.text = "/start"
    return message


def test_message_handlers(db, message_start):
    temp_user = StudentGroup.objects.create("someuser", "Fname", "Lname", "Password")
    temp_user.save()
    chat = Chat.objects.create(chat_id=1)
    chat.connected_user = temp_user
    chat.authorised = True
    chat.save()
    assert bot._test_message_handler(
        fetch_handler("cmd_start_handler"), message_start)
