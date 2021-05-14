from enum import Enum
from .chat import Chat

class State(Enum):
    CHAT_STARTED = 1
    NO_ACTIONS = 4
    SIGNING_IN_UNAME = 2
    SIGNING_IN_PASS = 2
    SIGNING_IN_CONFIRM_PASS = 2
    LOGING_IN_PASS = 5
    LOGING_IN_UNAME = 3


def onstate(chat_id: Chat, enum_state: State) -> bool:
    try:
        return Chat.objects.get(chat_id=chat_id).state == enum_state.value
    except Exception:
        return False

def authorized(chat_id: Chat) -> bool:
    try:
        return Chat.objects.get(chat_id=chat_id).authorised
    except Exception:
        return False