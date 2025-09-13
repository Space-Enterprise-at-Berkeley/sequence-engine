from states import AutoventStates as States

class Autovent:
    AV_THRESHOLD = 500.0
    AV_OVERPRESSURE_COUNT_LIMIT = 5

    currState = States.AWAIT_PRESSURE
    tankPressure = 0.0
    overPressureCount = 0

    def __init__(self, board):

        pass

    # run autovent
    def run(self):
        while(1):
            match currState:
                case States.AWAIT_PRESSURE:
                    pass

                case States.CHECK_THRESHOLD:
                    # open gems if pressure above threshold
                    if self.tankPressure >= self.AV_THRESHOLD:
                        self.overPressureCount += 1
                        if self.overPressureCount > self.AV_OVERPRESSURE_COUNT_LIMIT:
                            currState = States.SEND_ABORT
                        else:
                            currState = States.SEND_OPEN
                    else:
                        currState = States.SEND_CLOSE

                case States.SEND_OPEN:
                    self.AVOpenGems()

                case States.SEND_CLOSE:
                    self.AVCloseGems()
                    currState = States.AWAIT_PRESSURE

                case States.SEND_ABORT:
                    self.AVSendAbort()

    # sends open packet to gems
    def AVOpenGems(self):
        pass

    # sends close packet to gems
    def AVCloseGems(self):
        pass

    # sends abort packet
    def AVSendAbort(self):
        pass

    
    

