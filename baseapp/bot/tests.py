import sys

sys.path.append('../')

REDIS_TESTS = False

import os
import time

import pytest

import telebot
from telebot import types
from .handlers.common_objects import bot

if REDIS_TESTS:
    from telebot.handler_backends import RedisHandlerBackend



@pytest.fixture()
def telegram_bot():
    return telebot.TeleBot('', threaded=False)


@pytest.fixture
def private_chat():
    return types.Chat(id=11, type='private')


@pytest.fixture
def user():
    return types.User(id=10, is_bot=False, first_name='Some User')


@pytest.fixture()
def message(user, private_chat):
    params = {'text': '/start'}
    return types.Message(
        message_id=1, from_user=user, date=None, chat=private_chat, content_type='text', options=params, json_string=""
    )


@pytest.fixture()
def reply_to_message(user, private_chat, message):
    params = {'text': '/start'}
    reply_message = types.Message(
        message_id=2, from_user=user, date=None, chat=private_chat, content_type='text', options=params, json_string=""
    )
    reply_message.reply_to_message = message
    return reply_message


@pytest.fixture()
def update_type(message):
    edited_message = None
    channel_post = None
    edited_channel_post = None
    inline_query = None
    chosen_inline_result = None
    callback_query = None
    shipping_query = None
    pre_checkout_query = None
    poll = None
    poll_answer = None
    return types.Update(1001234038283, message, edited_message, channel_post, edited_channel_post, inline_query,
                        chosen_inline_result, callback_query, shipping_query, pre_checkout_query, poll, poll_answer)


@pytest.fixture()
def reply_to_message_update_type(reply_to_message):
    edited_message = None
    channel_post = None
    edited_channel_post = None
    inline_query = None
    chosen_inline_result = None
    callback_query = None
    shipping_query = None
    pre_checkout_query = None
    poll = None
    poll_answer = None
    return types.Update(1001234038284, reply_to_message, edited_message, channel_post, edited_channel_post,
                        inline_query,
                        chosen_inline_result, callback_query, shipping_query, pre_checkout_query, poll, poll_answer)


def next_handler(message):
    message.text = 'entered next_handler'