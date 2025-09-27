from sequences.autovent import Autovent
from comms.packet_config import config
from comms.packet_comms import *
from config.system_config import SystemConfig
from comms.packet_buffer import PacketBuffer

import time


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
    read_packets_mc()
    PacketBuffer.buffer["PT_2"][2].print()
    #PacketBuffer.print()
    # for sequence in sequences:
    #     sequence.run(time.time())