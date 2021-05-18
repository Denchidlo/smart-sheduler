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


def group_member(chat_id: Chat) -> bool:
    try:
        chat = Chat.objects.get(chat_id=chat_id)
        user = chat.connected_user
        if user != None:
            if user.group != None:
                return True
        return False
    except:
        return False
