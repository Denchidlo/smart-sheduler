from enum import Enum

class State(Enum):
    CHAT_STARTED = 1

def onstate(state: int, enum_state: State) -> bool:
    return state == enum_state.value