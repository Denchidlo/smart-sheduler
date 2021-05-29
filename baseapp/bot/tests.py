from .handlers.login import login_password_input, login_username_input
from .handlers.schedule import weekday_input_handler
from .handlers.groups import (
    group_action_handler,
    group_requests_handler,
    group_user_list_creator,
    request_group_input,
    user_info_handler,
    user_request_desision,
    user_request_desision_handler,
)
from logging import exception
from .handlers.signin import *
import pytest
from random import randint as rand
from telebot import types, TeleBot
from telebot.apihelper import send_message
from .models import *
from .views import cmd_cancel_handler, cmd_start_handler, default_handler
from .services.bot_init import bot

from .handlers.authorised import *
from .handlers.unauthorised import *


RESPONCE_TG_ID = 0


def fetch_handler(name):
    el = next(filter(lambda el: el["function"].__name__ == name, bot.message_handlers))
    return el


def get_message_handler(message):
    for handler in bot.message_handlers:
        if bot._test_message_handler(handler, message):
            return handler
    return None


def get_callback_handler(message):
    for handler in bot.callback_query_handlers:
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


def process_callback(callback):
    handler = get_callback_handler(callback)
    try:
        handler["function"](callback)
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
def model_group(db):
    group = StudentGroup.objects.create(name="953503", course=2)
    yield group
    group.delete()


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


@pytest.fixture(scope="function")
def telegram_callback(db, telegram_message, telegram_user, telegram_chat):
    return types.CallbackQuery(
        123123, telegram_user, 1, telegram_chat, telegram_message
    )


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


class TestGroupCallbacksAndHandlers:
    def test_callbacks(db, model_group, model_user, model_chat, telegram_callback):
        telegram_callback.data = "group=953503|cmd=info|page=0"
        model_user.group = model_group
        model_user.save()
        model_chat.connected_user = model_user
        model_chat.authorised = True
        model_chat.save()
        handler = process_callback(telegram_callback)
        assert handler == group_user_list_creator

        telegram_callback.data = "group=953503|cmd=membership|page=0"
        handler = process_callback(telegram_callback)
        assert handler == group_requests_handler
        grouplead = GroupLead.objects.create(group=model_group, user=model_user)
        grouplead.save()
        handler = process_callback(telegram_callback)
        assert handler == group_requests_handler

        telegram_callback.data = f"group=953503|cmd=user_action|id={model_user.id}"
        handler = process_callback(telegram_callback)
        assert handler == user_request_desision

        telegram_callback.data = f"group=953503|cmd=user_kick|id={model_user.id}"
        handler = process_callback(telegram_callback)
        assert handler == user_request_desision_handler
        model_user = ScheduleUser.objects.get(id=model_user.id)
        assert model_user.group == None

        telegram_callback.data = f"group=953503|cmd=user_decline|id={model_user.id}"
        handler = process_callback(telegram_callback)
        assert handler == user_request_desision_handler
        model_user = ScheduleUser.objects.get(id=model_user.id)
        assert model_user.is_member == False

        model_user.group = model_group
        model_user.save()
        telegram_callback.data = f"group=953503|cmd=user_accept|id={model_user.id}"
        handler = process_callback(telegram_callback)
        assert handler == user_request_desision_handler
        model_user = ScheduleUser.objects.get(id=model_user.id)
        assert model_user.is_member == True

        telegram_callback.data = f"group=953503|cmd=user_makeadmin|id={model_user.id}"
        handler = process_callback(telegram_callback)
        assert handler == user_request_desision_handler
        model_user = ScheduleUser.objects.get(id=model_user.id)
        assert model_user.group.grouplead.user == model_user

        new_user = ScheduleUser.objects.create(
            username="Collision",
            first_name="Fname",
            last_name="Lname",
            password="111111",
        )
        new_user.group = model_group
        new_user.is_member == True
        new_user.save()
        telegram_callback.data = (
            f"group=953503|cmd=user_info|id={model_user.id}|return_page=0"
        )
        handler = process_callback(telegram_callback)
        assert handler == user_info_handler
        model_user = ScheduleUser.objects.get(id=model_user.id)

        telegram_callback.data = f"group=953503|cmd=stop"
        handler = process_callback(telegram_callback)
        assert handler == group_action_handler

        telegram_callback.data = f"group=953503|cmd=notify"
        handler = process_callback(telegram_callback)
        assert handler == group_action_handler

        telegram_callback.data = f"group=953503|cmd=leave"
        handler = process_callback(telegram_callback)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == group_action_handler
        assert model_user == model_chat.connected_user

        telegram_callback.data = f"group=953505|cmd=leave"
        handler = process_callback(telegram_callback)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == group_action_handler

        model_group.grouplead.user = None
        model_group.grouplead.save()
        model_user.group = None
        model_user.save()
        telegram_callback.data = f"group=953505|cmd=leave"
        handler = process_callback(telegram_callback)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == group_action_handler
        assert model_user.group == None

        model_chat = Chat.get_chat(model_chat.chat_id)
        request_group_input(model_chat, "953503")
        model_group = StudentGroup.objects.first()
        assert model_group.grouplead != None
        try:
            request_group_input(model_chat, "953505")
        except:
            assert True


class TestAuthorised:
    def test_auth_handlers(db, telegram_message, model_user, model_chat, model_group):
        model_user.group = model_group
        model_user.save()
        model_chat.connected_user = model_user
        model_chat.state = State.ON_ACCOUNT.value
        model_chat.authorised = True
        model_chat.save()
        telegram_message.text = "Edit username"
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert model_chat.state == State.ON_ACCOUNT_USERNAME_INPUT.value

        model_chat.state = State.ON_ACCOUNT.value
        model_chat.save()
        telegram_message.text = "Edit first and last name"
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == authorised_actions_handler

        model_chat.state = State.ON_ACCOUNT.value
        model_chat.save()
        telegram_message.text = "Edit password"
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == authorised_actions_handler
        assert model_chat.state == State.ON_ACCOUNT_PASSCHG_CONFIRM.value

        model_chat.state = State.ON_ACCOUNT.value
        model_chat.save()
        telegram_message.text = "Delete user"
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert model_chat.state == State.ON_ACCOUNT_DELETE.value

        model_chat.state = State.ON_ACTIONS.value
        model_chat.save()
        telegram_message.text = "Request group membership"
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert model_chat.state == State.ON_GROUP_REQUEST_NAME.value

        model_chat.state = State.ON_ACTIONS.value
        model_chat.save()
        telegram_message.text = "Bwer"
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert model_chat.state == State.ON_ACTIONS.value

        model_chat.state = State.NO_ACTIONS.value
        model_chat.save()
        telegram_message.text = "Account 📝"
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert model_chat.state == State.ON_ACCOUNT.value

        model_chat.state = State.NO_ACTIONS.value
        model_chat.save()
        telegram_message.text = "Actions 📋"
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert model_chat.state == State.ON_ACTIONS.value

        model_chat.state = State.ON_ACTIONS.value
        model_chat.save()
        telegram_message.text = "Get schedule"
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert model_chat.state == State.ON_ACTION_SCHEDULE_GROUP_ENTER.value

        model_chat.state = State.ON_ACTIONS.value
        model_chat.save()
        grouplead = GroupLead.objects.create(group=model_group, user=model_user)
        grouplead.save()
        telegram_message.text = "Group"
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == authorised_actions_handler
        assert model_chat.state == State.ON_ACTIONS.value


class TestSchedule:
    def test_schedule_handlers(
        db, model_group, model_user, model_chat, telegram_callback, telegram_chat
    ):
        telegram_callback.data = "group=953503|day=2"
        model_user.group = model_group
        model_user.save()
        model_chat.connected_user = model_user
        model_chat.authorised = True
        model_chat.save()
        handler = process_callback(telegram_callback)
        assert handler == weekday_input_handler

        telegram_callback.data = "group=953503|day=2|week=2"
        handler = process_callback(telegram_callback)

        schedule_group_input(model_chat, "953503")
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert model_chat.state == State.NO_ACTIONS.value


class TestLoginHandlers:
    @pytest.mark.parametrize(
        "pre_state, message, handler, new_state",
        [
            (
                State.LOGING_IN_UNAME.value,
                "Testuser",
                login_username_input,
                State.LOGING_IN_PASS.value,
            ),
            (
                State.LOGING_IN_PASS.value,
                "passwoasd123rd",
                login_password_input,
                State.LOGING_IN_UNAME.value,
            ),
        ],
    )
    def test_login_uname_input(
        self,
        pre_state,
        message,
        handler,
        new_state,
        db,
        model_group,
        model_user,
        model_chat,
        telegram_message,
        telegram_chat,
    ):
        model_chat.state = pre_state
        model_user.set_password("password")
        model_user.save()
        model_chat.connacted_user = model_user
        model_chat.save()
        telegram_message.text = message
        handler = process_message(telegram_message)
        model_chat = Chat.get_chat(model_chat.chat_id)
        assert handler == handler
        assert model_chat.state == new_state
