from enum import Enum
from typing import Iterable
from .chat import Chat


class State(Enum):
    CHAT_STARTED = 1
    NO_ACTIONS = 2
    SIGNING_IN_UNAME = 3
    SIGNING_IN_FNAME = 4
    SIGNING_IN_LNAME = 5
    SIGNING_IN_PASS = 6
    SIGNING_IN_CONFIRM_PASS = 7
    LOGING_IN_PASS = 8
    LOGING_IN_UNAME = 9
    ON_ACTIONS = 10
    ON_GROUP_REQUEST_NAME = 12
    ON_ACTION_SCHEDULE_GROUP_ENTER = 13
    ON_ACTION_NOTIFY = 14
    ON_ACCOUNT = 15
    ON_ACCOUNT_DELETE = 16
    ON_ACCOUNT_USERNAME_INPUT = 17
    ON_ACCOUNT_FULLNAME_INPUT = 18
    ON_ACCOUNT_PASSCHG_CONFIRM = 19
    ON_ACCOUNT_PASSCHG_INPUT = 20


def onstate(chat_id: Chat, enum_states) -> bool:
    try:
        state = Chat.objects.get(chat_id=chat_id).state
        return state in [el.value for el in enum_states]
    except:
        return False


def authorized(chat_id: Chat) -> bool:
    try:
        return Chat.objects.get(chat_id=chat_id).authorised
    except:
        return False
