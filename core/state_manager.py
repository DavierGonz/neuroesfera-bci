from enum import Enum


class AppState(Enum):
    MENU = 1
    PROTOCOL_SETUP = 2
    PROTOCOL_READY = 3
    SESSION_COMPLETE = 4
