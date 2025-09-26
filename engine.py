from autovent import Autovent
from comms.packet_config import config
import time
from config.system_config import SystemConfig

def autovent_init():
    # build nos autovent sequence
    if SystemConfig.boards["AC_NOS_BOARD"] is not None:
        sequences.append(Autovent(
            ac_board = SystemConfig.boards["AC_NOS_BOARD"],
            ac_channel = SystemConfig.channels["AC_NOS_GEMS"],
            pt_board = SystemConfig.boards["PT_NOS_BOARD"],
            pt_channel = SystemConfig.channels["PT_NOS_TANK"],
            uptime = uptime,
            cycletime = AUTOVENT_CYCLE_TIME,
            duty_cycletime = AUTOVENT_DUTY_CYCLE_TIME,
            nos = True
        ))

    # build ipa autovent sequence
    if SystemConfig.boards["AC_IPA_BOARD"] is not None:
        sequences.append(Autovent(
            ac_board = SystemConfig.boards["AC_IPA_BOARD"],
            ac_channel = SystemConfig.channels["AC_IPA_GEMS"],
            pt_board = SystemConfig.boards["PT_IPA_BOARD"],
            pt_channel = SystemConfig.channels["PT_IPA_TANK"],
            uptime = uptime,
            cycletime = AUTOVENT_CYCLE_TIME,
            duty_cycletime = AUTOVENT_DUTY_CYCLE_TIME,
            nos = False
        ))

# -----------------------------------------------------
#
# main loop
#
# -----------------------------------------------------

AUTOVENT_CYCLE_TIME = 5
AUTOVENT_DUTY_CYCLE_TIME = 100

uptime = time.time()
sequences = []

autovent_init()

while True:
    for sequence in sequences:
        sequence.run(time.time())