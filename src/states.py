from enum import Enum

# ENUMERATE STATES BY INDEX 0 TO SUPPORT ADJACENCY MATRIX CONSTRUCTION
class AutoventStates(Enum):
        AWAIT_PRESSURE = 0
        CHECK_THRESHOLD = 1
        SEND_OPEN = 2
        SEND_CLOSE = 3
        SEND_ABORT = 4