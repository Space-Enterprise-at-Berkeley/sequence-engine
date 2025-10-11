from config.states import SerialBridgeStates as States
from comms.packet import Packet

class SerialBridge:
    def __init__(self, ac_board, ac_channel, pt_board, pt_channel, uptime, cycletime, duty_cycletime, nos):
        self.name = "AUTOVENT"
        self.is_nos = nos
        
        self.AV_THRESHOLD = 500.0
        self.AV_OVERPRESSURE_COUNT_LIMIT = 5
        self.DUTY_SAMPLE_SIZE = 600 # size of duty buffer
        self.CYCLE_TIME = cycletime # autovent cycle time, in ms
        self.DUTY_CYCLE_TIME = duty_cycletime

        # board/channel defs
        self.AC_BOARD = ac_board
        self.AC_CHANNEL = ac_channel
        self.PT_BOARD = pt_board
        self.PT_CHANNEL = pt_channel

        self.curr_state = States.BELOW_THRESHOLD
        self.tank_pressure = 0.0
        self.over_pressure_count = 0

        # handles cycle times
        self.uptime = uptime
        self.cooldown = 0
        self.duty_cycle_cooldown = 0
        
        # duty cycle
        self.duty_buffer = [0] * self.DUTY_SAMPLE_SIZE
        self.buffer_index = -1

        print(f"built {"NOS" if self.is_nos else "IPA"} autovent on {self.AC_BOARD} channel {self.AC_CHANNEL}, reading {self.PT_BOARD} channel {self.PT_CHANNEL}")

        pass

    # run autovent
    def run(self, uptime):
        dt = uptime - self.uptime
        self.uptime = uptime

        self.cooldown -= dt
        self.duty_cycle_cooldown -= dt

        self.buffer_index += 1
        if self.buffer_index == self.DUTY_SAMPLE_SIZE:
            self.buffer_index = 0

        if(self.cooldown > 0): return

        return_packet = None
        duty_cycle_packet = None
        db_packet = None

        # get latest tank pressure packet
        

        # open gems if pressure above threshold
        if tank_pressure >= self.AV_THRESHOLD:
            self.currState = States.ABOVE_THRESHOLD
            self.over_pressure_count += 1

            if self.over_pressure_count > self.AV_OVERPRESSURE_COUNT_LIMIT:
                return_packet = self.av_send_abort()
            else:
                self.duty_buffer[self.buffer_index] = 1
                self.av_open_gems()

        else:
            self.currState = States.BELOW_THRESHOLD
            self.duty_buffer[self.buffer_index] = 0
            self.av_close_gems()

        if self.duty_cycle_cooldown <= 0:
            self.duty_cycle()
            self.duty_cycle_cooldown = self.DUTY_CYCLE_TIME

        self.cooldown = self.CYCLE_TIME

    # calculate and send duty cycle packet 
    def duty_cycle(self):
        avg = sum(self.duty_buffer)
        avg *= 100.0 / self.DUTY_SAMPLE_SIZE

        duty_packet = Packet()
        duty_packet.board = "GD"
        duty_packet.id = 8
        duty_packet.field = {
            "gemsDutyCycle": avg
        }
        duty_packet.send()


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

    
    

