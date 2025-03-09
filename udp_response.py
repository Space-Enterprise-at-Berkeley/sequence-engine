import socket
import struct # pack and unpack byte arrays
import sys
import warnings

from packet_config import Config

# i put all the packet spec json parsing in a separate file
config = Config()

# enum: only exists if values are enums
# length: how many values are in data
# values: array of packet data
class PacketData:
    def __init__(self):
        self.enum = ""
        self.length = 0
        self.values = []

# fields: dictionary of { symbol, PacketData }
#         for each line item of a packet type in types.jsonc
class Packet:
    def __init__(self):
        self.fields = {}
        self.timestamp = 0
        self.error = True
        self.board = ""
        self.id = -1

    def print(self):
        if self.error == True:
            print("Error: Cannot read packet")
        else:
            print(f"{self.board} board, packet id {self.id}")
            for name, field in self.fields.items():
                print(f"{config.packets[self.board][self.id]} ({name}): ", end = '')
                if len(field.enum) != 0:
                    print(f"(enum {field.enum})")
                else:
                    print()
                print(f"{field.values}:")
            print()

# idk https://en.wikipedia.org/wiki/Fletcher%27s_checksum
def fletcher16(data):
	a = 0
	b = 0
	for i in range(len(data)):
		a = (a + data[i]) % 256
		b = (b + a) % 256
	return a | (b << 8)

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
    packet.id = id
    
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

    packet.fields = parse_data(field_data, config.packets[board][id])

    packet.error = False
    packet.print()

# parse data field based on packet data type
def parse_data(data, type):
    fields = {}
    for item in config.types[type]:
        field = PacketData()
        length = 1
        if "array" in item:
            length = item["array"]

        # parse byte array based on data type, ref struct lib
        match item["type"]:
            case "u8":
                format = "B" * length
            case "u16":
                format = "S" * length
            case "u32":
                format = "I" * length
            case "f32":
                format = "f" * length

        field.values = list(struct.unpack_from(format, data))
        field.length = length

        if "enum" in item:
            field.enum = item["enum"]

        fields[item["symbol"]] = field

    return fields

# require host ip argument
if len(sys.argv) < 2:
    print("Missing IP argument")
    sys.exit()

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
    data, addr = mc_sock.recvfrom(1024)
    parse_packet(data, addr)

