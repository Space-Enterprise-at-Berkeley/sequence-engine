import socket
import struct
import sys
import json
import re
import warnings
import fnmatch
import pprint

class Packet:
    def __init__(self):
        self.fields = {}
        self.timestamp = 0
        self.error = True
        self.board = ""
        self.id = -1

class Config:
    def __init__(self):
        self.boards = {}
        self.ip_lookup = {}
        self.packets = {}

config = Config()

# idk https://en.wikipedia.org/wiki/Fletcher%27s_checksum
def fletcher16(data):
	a = 0
	b = 0
	for i in range(len(data)):
		a = (a + data[i]) % 256
		b = (b + a) % 256
	return a | (b << 8)

# read config.jsonc
with open("universalproto/config.jsonc") as c:
    # zander gave me this regex, goat
    real_json = re.sub(r"(\/\/.*?\n|\/\*.*?\*\/)", r"", c.read(), flags=re.DOTALL) # remove all comments from config.jsonc
    config_json = json.loads(real_json)

# read packets.jsonc
with open("universalproto/packets.jsonc") as p:
    real_json = re.sub(r"(\/\/.*?\n|\/\*.*?\*\/)", r"", p.read(), flags=re.DOTALL) # remove all comments from config.jsonc
    packets_json = json.loads(real_json)

# flip deviceIDs and put into config.boards
for board, id in config_json["deviceIds"].items():
    config.boards.update({str(id): board})
    config.ip_lookup.update({board: str(id)})
    config.packets[board] = {}
        
# add packet ids to config.packets
for packet in packets_json:
    for writer in packet["writes"]:
        for board_name in config.ip_lookup:
            if fnmatch.fnmatch(board_name, writer):
                if "payload" in packet:
                    config.packets[board_name].update({str(packet["id"]): packet["payload"]})

# under construction, parse packet data
# ref: struct.unpack_from() https://docs.python.org/3/library/struct.html
def parse_packet(data, addr):
    packet = Packet()

    # parse packet data into variables
    boardID = addr[0][-2:]
    unpack = struct.unpack_from("<BBIH", data[0:8])
    id = str(unpack[0]) # from what i have seen id should be a str
    length = unpack[1]
    run_time = unpack[2]
    checksum = unpack[3]

    # add board name to packet
    if boardID not in config.boards: # confirm packet board id
        warnings.warn(f"Warning: IP {addr[0]} not recognized")
        packet.error = True
        return packet
    
    board = config.boards[boardID]
    packet.board = board
    
    # parse actual data and calculate checksum
    unpack = struct.unpack_from(f"<{6}sH{length}s", data)
    field_data = unpack[2]
    expected_checksum = fletcher16(unpack[0] + unpack[2])
    
    # confirm checksum validity
    if not expected_checksum == checksum:
        warnings.warn(f"Warning: Invalid checksum from {board} (packet id {id})")
        packet.error = True
        return packet

    # confirm packet id validity
    if not id in config.packets[board]:
        warnings.warn(f"Warning: Unrecognized packet {id} on {board}")
        print(config.packets[board])
        packet.error = True
        return packet

    return 0

# require host ip argument
if len(sys.argv) < 2:
    print("Missing IP argument")
    sys.exit()

#UDP_IP = "127.0.0.1"
BCAST_PORT = 42099
MCAST_PORT = 42080

#define ips
host = socket.inet_aton(f"10.0.0.{sys.argv[1]}")
mcast_ip = socket.inet_aton("224.0.0.3")

# create broadcast UDP socket
bc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
bc_sock.bind(("", BCAST_PORT))

# create multicast UDP socket
mc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
mc_sock.bind(("", MCAST_PORT))

# add host to multicast group, requires packing into ip_mreqn struct
# ref https://man7.org/linux/man-pages/man7/ip.7.html
mreq = struct.pack("=4s4s", mcast_ip, host)
mc_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"Listening for UDP packets on port {BCAST_PORT}")

while True:
    # receive data

    # data, addr = bc_sock.recvfrom(1024)
    # print(f"Received broadcast packet from {addr}: {data.decode('utf-8')}")
    # print("bobr")

    data, addr = mc_sock.recvfrom(1024)
    # print(f"Received multicast packet from {addr[0]}:{addr[1]}: " + data.hex(" ") + '\n')
    parse_packet(data, addr)

