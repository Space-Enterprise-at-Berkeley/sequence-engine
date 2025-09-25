from states import AutoventStates as States
from comms.packet import Packet
class Autovent:
    def __init__(self, board, channel):
        self.AV_THRESHOLD = 500.0
        self.AV_OVERPRESSURE_COUNT_LIMIT = 5

        self.BOARD = board
        self.CHANNEL = channel

        self.curr_state = States.AWAIT_PRESSURE
        self.tank_pressure = 0.0
        self.over_pressure_count = 0

        pass

    # run autovent
    def run(self):
        match currState:
            case States.AWAIT_PRESSURE:
                pass

            case States.CHECK_THRESHOLD:
                # open gems if pressure above threshold
                if self.tank_pressure >= self.AV_THRESHOLD:
                    self.over_pressure_count += 1
                    if self.over_pressure_count > self.AV_OVERPRESSURE_COUNT_LIMIT:
                        currState = States.SEND_ABORT
                    else:
                        currState = States.SEND_OPEN
                else:
                    currState = States.SEND_CLOSE

            case States.SEND_OPEN:
                self.av_open_gems()

            case States.SEND_CLOSE:
                self.av_close_gems()
                currState = States.AWAIT_PRESSURE

            case States.SEND_ABORT:
                self.av_send_abort()

    # sends open packet to gems
    def av_open_gems(self):
        open_packet = Packet()
        open_packet.board = self.BOARD
        open_packet.id = 100
        open_packet.fields = {
            "actuatorNumber": self.CHANNEL,
            "action": "ON",
            "actuateTime": 0
        }
        open_packet.send()

    # sends close packet to gems
    def av_close_gems(self):
        close_packet = Packet()
        close_packet.board = self.BOARD
        close_packet.id = 100
        close_packet.fields = {
            "actuatorNumber": self.CHANNEL,
            "action": "OFF",
            "actuateTime": 0
        }
        close_packet.send()

    # sends abort packet
    # TO DO: ABORTS SHOULD SEND OVER BROADCAST (PACKET.PY UPDATE)
    def av_send_abort(self):
        abort_packet = Packet()
        abort_packet.board = self.BOARD
        abort_packet.id = 133
        abort_packet.fields = {
            "systemMode": "COLDFLOW", # NEED GLOBAL SE SYSTEMMODE MAYBE
            "abortReason": "NOS_OVERPRESSURE" # NEED MEMBER BOOL TO SEE IF NOS OR IPA
        }
        abort_packet.send()

    
    

