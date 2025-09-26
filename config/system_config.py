from comms.packet_config import config

class SystemConfig:
    channels = {
        "AC_NOS_GEMS": -1,
        "AC_IPA_GEMS": -1,
        "PT_NOS_TANK": -1,
        "PT_IPA_TANK": -1
    }

    boards = {
        "AC_NOS_BOARD": None,
        "AC_IPA_BOARD": None,
        "PT_NOS_BOARD" : None,
        "PT_IPA_BOARD": None,
    }

    def __init__(self):
        self.autovent_init()

    def autovent_init(self):
        for name, channels in config.channels.items():
            nos_channel = next((item["channel"] for item in channels if item["measure"] == "AC_NOS_GEMS"), None)
            ipa_channel = next((item["channel"] for item in channels if item["measure"] == "AC_IPA_GEMS"), None)
            nos_tank = next((item["channel"] for item in channels if item["measure"] == "PT_NOS_TANK"), None)
            ipa_tank = next((item["channel"] for item in channels if item["measure"] == "PT_IPA_TANK"), None)

            if nos_channel is not None:
                SystemConfig.boards["AC_NOS_BOARD"] = name
                SystemConfig.channels["AC_NOS_GEMS"] = nos_channel

            if ipa_channel is not None:
                SystemConfig.boards["AC_IPA_BOARD"] = name
                SystemConfig.channels["AC_IPA_GEMS"] = ipa_channel

            if nos_tank is not None:
                SystemConfig.boards["PT_NOS_BOARD"] = name
                SystemConfig.channels["PT_NOS_TANK"] = nos_tank

            if ipa_tank is not None:
                SystemConfig.boards["PT_IPA_BOARD"] = name
                SystemConfig.channels["PT_IPA_TANK"] = ipa_tank
            
system_config = SystemConfig()