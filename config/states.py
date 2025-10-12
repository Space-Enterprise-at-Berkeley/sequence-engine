from enum import Enum

class AutoventStates(Enum):
        BELOW_THRESHOLD = 0
        ABOVE_THRESHOLD = 1
        ABORTED = 2

class SerialBridgeStates(Enum):
        READING = 0
        ABORTED = 1