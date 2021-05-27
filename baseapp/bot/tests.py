from .handlers.signin import *
import pytest
from random import randint as rand
from telebot import types, TeleBot
from telebot.apihelper import send_message
from .models import *
from .views import cmd_cancel_handler, cmd_start_handler, default_handler
from .services.bot_init import bot


RESPONCE_TG_ID = 0


def fetch_handler(name):
    el = next(filter(lambda el: el["function"].__name__ == name, bot.message_handlers))
    return el


def get_message_handler(message):
    for handler in bot.message_handlers:
        if bot._test_message_handler(handler, message):
            return handler
    return None


def process_message(message):
    handler = get_message_handler(message)
    try:
        handler["function"](message)
    except:
        pass
    return handler["function"]


@pytest.fixture(scope="function")
def model_user(db):
    user = ScheduleUser.objects.create(
        username="Testuser",
        first_name="testname",
        last_name="testname",
        password="password",
    )
    user.save()
    yield user
    user.delete()


@pytest.fixture(scope="function")
def model_chat(db):
    chat = Chat.objects.create(
        chat_id=RESPONCE_TG_ID,
        connected_user=None,
        authorised=False,
        state=State.CHAT_STARTED.value,
    )
    chat.save()
    yield chat
    chat.delete()


@pytest.fixture(scope="function")
def telegram_chat(db) -> types.Chat:
    return types.Chat(RESPONCE_TG_ID, "private")


@pytest.fixture(scope="function")
def telegram_user(db) -> types.User:
    return types.User(228322, False, "Testname")


@pytest.fixture(scope="function")
def telegram_message(db, telegram_user, telegram_chat) -> types.Message:
    return types.Message(123123, telegram_user, 1, telegram_chat, "text", [], "null")


class TestViewHandlers:
    def test_cmd_start_handler(db, telegram_message, model_user, model_chat):
        telegram_message.text = "/start"
        # Case unauthorised
        handler = process_message(telegram_message)
        assert handler == cmd_start_handler
        assert Chat.objects.get(chat_id=RESPONCE_TG_ID) != None
        # Case authorised
        model_chat.connected_user = model_user
        model_chat.authorised = True
        handler = process_message(telegram_message)
        assert handler == cmd_start_handler

    def test_cmd_cancel_handler(db, telegram_message, model_user, model_chat):
        telegram_message.text = "/cancel"
        # Case input cancelation
        model_chat.connected_user = model_user
        model_chat.authorised = False
        model_chat.state = State.SIGNING_IN_CONFIRM_PASS.value
        model_chat.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == cmd_cancel_handler
        assert model_chat.connected_user == None
        assert model_chat.state == State.NO_ACTIONS.value
        # Case usual cancelation
        model_chat.connected_user = None
        model_chat.authorised = False
        model_chat.state = State.ON_ACTIONS.value
        model_chat.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == cmd_cancel_handler
        assert model_chat.connected_user == None
        assert model_chat.state == State.NO_ACTIONS.value

    def test_default_handler(db, telegram_message, model_user, model_chat):
        for content_type in [
            "audio",
            "photo",
            "voice",
            "video",
            "document",
            "location",
            "contact",
            "sticker",
        ]:
            telegram_message.content_type = content_type
            model_chat.connected_user = model_user
            model_chat.authorised = True
            model_chat.state = rand(1, 14)
            model_chat.save()
            handler = process_message(telegram_message)
            assert handler == default_handler


class TestSignupHandlers:
    def test_signup_input_username_handler(
        db, telegram_message, model_user, model_chat
    ):
        # Invalid username
        telegram_message.text = "username@!#!@()!!!112123 sdas"
        model_chat.state = State.SIGNING_IN_UNAME.value
        model_chat.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == signin_data_input
        assert model_chat.state == State.SIGNING_IN_UNAME.value
        assert model_chat.connected_user == None

        # User already exsits
        telegram_message.text = "Collision"
        collision_user = ScheduleUser.objects.create(
            username="Collision",
            first_name="Fname",
            last_name="Lname",
            password="111111",
        )
        collision_user.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == signin_data_input
        assert model_chat.state == State.SIGNING_IN_UNAME.value
        assert model_chat.connected_user == None
        collision_user.delete()

        # Everything is ok
        username = "GoodJob"
        telegram_message.text = username
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == signin_data_input
        assert model_chat.connected_user != None and model_chat.authorised == False
        assert model_chat.connected_user.username == username
        assert model_chat.state == State.SIGNING_IN_FNAME.value

    def test_singup_input_fname_handler(db, telegram_message, model_user, model_chat):
        # Invalid first name
        name = "123Vitya"
        template_name = model_user.first_name
        telegram_message.text = name
        model_chat.connected_user = model_user
        model_chat.state = State.SIGNING_IN_FNAME.value
        model_chat.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == signin_data_input
        assert model_chat.connected_user != None and model_chat.authorised == False
        assert model_chat.connected_user.first_name == template_name
        assert model_chat.state == State.SIGNING_IN_FNAME.value

        # Everything is ok
        name = "Vitya"
        telegram_message.text = name
        model_chat.connected_user = model_user
        model_chat.state = State.SIGNING_IN_FNAME.value
        model_chat.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == signin_data_input
        assert model_chat.connected_user != None and model_chat.authorised == False
        assert model_chat.connected_user.first_name == name
        assert model_chat.state == State.SIGNING_IN_LNAME.value

    def test_singup_input_fname_handler(db, telegram_message, model_user, model_chat):
        # Invalid last name
        name = "123Ivanov"
        template_name = model_user.last_name
        telegram_message.text = name
        model_chat.connected_user = model_user
        model_chat.state = State.SIGNING_IN_LNAME.value
        model_chat.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == signin_data_input
        assert model_chat.connected_user != None and model_chat.authorised == False
        assert model_chat.connected_user.last_name == template_name
        assert model_chat.state == State.SIGNING_IN_LNAME.value

        # Everything is ok
        name = "Ivanov"
        telegram_message.text = name
        model_chat.connected_user = model_user
        model_chat.state = State.SIGNING_IN_LNAME.value
        model_chat.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == signin_data_input
        assert model_chat.connected_user != None and model_chat.authorised == False
        assert model_chat.connected_user.last_name == name
        assert model_chat.state == State.SIGNING_IN_PASS.value

    def test_singup_input_pass_handler(db, telegram_message, model_user, model_chat):
        # Invalid pass
        password = "123ivanovvitya"
        telegram_message.text = password
        model_user.set_password("asdfsd")
        model_user.save()
        model_chat.connected_user = model_user
        model_chat.state = State.SIGNING_IN_PASS.value
        model_chat.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == signin_password_input
        assert model_chat.connected_user != None and model_chat.authorised == False
        assert model_chat.connected_user.check_password("asdfsd")
        assert model_chat.state == State.SIGNING_IN_PASS.value

        # Everything is ok
        password = "123VSvanovvitya#"
        telegram_message.text = password
        model_chat.connected_user = model_user
        model_chat.state = State.SIGNING_IN_PASS.value
        model_chat.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == signin_password_input
        assert model_chat.connected_user != None and model_chat.authorised == False
        assert model_chat.connected_user.check_password(password)
        assert model_chat.state == State.SIGNING_IN_CONFIRM_PASS.value

    def test_singup_confirm_pass_handler(db, telegram_message, model_user, model_chat):
        password = "123ivanovvitya"
        telegram_message.text = password
        model_user.set_password("123VSvanovvitya#")
        model_user.save()
        model_chat.connected_user = model_user
        model_chat.state = State.SIGNING_IN_CONFIRM_PASS.value
        model_chat.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == signin_password_input
        assert model_chat.connected_user != None and model_chat.authorised == False
        assert model_chat.state == State.SIGNING_IN_CONFIRM_PASS.value

        # Everything is ok
        password = "123VSvanovvitya#"
        telegram_message.text = password
        model_chat.connected_user = model_user
        model_chat.state = State.SIGNING_IN_CONFIRM_PASS.value
        model_chat.save()
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == signin_password_input
        assert model_chat.connected_user != None and model_chat.authorised == True
        assert model_chat.state == State.NO_ACTIONS.value


class TestCallback:
    def test_callback(db):
        assert 0
