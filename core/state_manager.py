from enum import Enum


class AppState(Enum):
    MENU = 1
    PARADIGM_MENU = 2
    PROTOCOL_SETUP = 3
    PROTOCOL_READY = 4
    SESSION_COMPLETE = 5
