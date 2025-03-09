import re
import json
import fnmatch # filename matching in packets.jsonc

class Config:
    def __init__(self):
        self.boards = {}
        self.ip_lookup = {}
        self.packets = {}
        self.types = {}

        # zander gave me this regex, goat
        regex = r"(\/\/.*?\n|\/\*.*?\*\/)"

        # read config.jsonc
        with open("universalproto/config.jsonc") as c:
            # removes all comments from config.jsonc
            real_json = re.sub(regex, r"", c.read(), flags=re.DOTALL)
            config_json = json.loads(real_json)

        # read packets.jsonc
        with open("universalproto/packets.jsonc") as p:
            real_json = re.sub(regex, r"", p.read(), flags=re.DOTALL)
            packets_json = json.loads(real_json)

        # read types.jsonc
        with open("universalproto/types.jsonc") as t:
            real_json = re.sub(regex, r"", t.read(), flags=re.DOTALL)
            types_json = json.loads(real_json)

        # flip deviceIDs and put into config.boards
        for board, id in config_json["deviceIds"].items():
            self.boards[str(id)] = board
            self.ip_lookup[board] = str(id)
            self.packets[board] = {}
                
        # add packet ids to config.packets
        for packet in packets_json:
            for writer in packet["writes"]:
                for board_name in self.ip_lookup:
                    if fnmatch.fnmatch(board_name, writer):
                        if "payload" in packet:
                            self.packets[board_name][str(packet["id"])] = packet["payload"]

        # add types to config.types
        for name, type in types_json.items():
            self.types[name] = type