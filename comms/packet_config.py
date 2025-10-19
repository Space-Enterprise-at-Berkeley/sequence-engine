import re
import json
import fnmatch # filename matching in packets.jsonc

PACKET_SPEC_PATH = "universalproto/"

class Board:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.writes = {}
        self.reads = {}

# parses packet spec json into Config object
class Config:
    def __init__(self):
        self.board_to_id = {} # dictionary {board name: id}
        self.id_to_board = {} # dictionary {id: board name}

        self.boards = {} # dictionary {board name: Board object}
        self.types = {}
        self.channels = {}

        # zander gave me this regex, goat
        regex = r"(\/\/.*?\n|\/\*.*?\*\/)"

        # read config.jsonc
        with open(PACKET_SPEC_PATH + "config_cart.jsonc") as c:
            # removes all comments from config.jsonc
            real_json = re.sub(regex, r"", c.read(), flags=re.DOTALL)
            config_json = json.loads(real_json)

        # read packets.jsonc
        with open(PACKET_SPEC_PATH +  "packets.jsonc") as p:
            real_json = re.sub(regex, r"", p.read(), flags=re.DOTALL)
            packets_json = json.loads(real_json)

        # read types.jsonc
        with open(PACKET_SPEC_PATH + "types.jsonc") as t:
            real_json = re.sub(regex, r"", t.read(), flags=re.DOTALL)
            types_json = json.loads(real_json)

        # flip deviceIDs and put into config.boards
        for board, id in config_json["deviceIds"].items():
            new_board = Board(board, id)
            self.boards[board] = new_board

            self.id_to_board[id] = board
            self.board_to_id[board] = id
                
        # add packet ids to config.packets
        for packet in packets_json:
            for board in self.boards.values():
                for writer in packet["writes"]:
                        if fnmatch.fnmatch(board.name, writer):
                            if "payload" in packet:
                                # add packet type to board.writes
                                board.writes[packet["id"]] = {
                                    "name": packet["name"],
                                    "payload": packet["payload"]
                                }
                for reader in packet["reads"]:
                        if fnmatch.fnmatch(board.name, reader):
                            if "payload" in packet:
                                # add packet type to board.reads
                                board.reads[packet["id"]] = {
                                    "name": packet["name"],
                                    "payload": packet["payload"]
                                }

        # add types to config.types
        for name, type in types_json.items():
            self.types[name] = type

        # add channel mappings to config.channels
        for name, channels in config_json.items():
            if name == "deviceIds" or name == "version":
                continue
            self.channels[name] = channels

config = Config()
print(config.boards["FC_1"].reads)