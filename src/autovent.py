from states import AutoventStates as States

class Autovent:
    def __init__(self, board, channel):
        self.AV_THRESHOLD = 500.0
        self.AV_OVERPRESSURE_COUNT_LIMIT = 5

        self.BOARD_ID = board
        self.CHANNEL = channel

        self.curr_state = States.AWAIT_PRESSURE
        self.tank_pressure = 0.0
        self.over_pressure_count = 0

        pass

    # run autovent
    def run(self):
        while(1):
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
        pass

    # sends close packet to gems
    def av_close_gems(self):
        pass

    # sends abort packet
    def av_send_abort(self):
        pass

    
    

