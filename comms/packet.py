import socket
import struct # pack and unpack byte arrays
import sys
import warnings
from enum import Enum

from comms.packet_config import config

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
        self.name = ""

    def print(self):
        if self.error == True:
            print("Error: Cannot read packet")
        else:
            print()
            print(f"**{self.board.writes[self.id]["name"]} packet (id {self.id}) sent from {self.board.name} board**")
            for name, field in self.fields.items():
                print(f"{name}", end = '')

                if field.enum != "": # parse enum key from value
                    enum = next(k for k, v in config.types[field.enum].items() if v == field.values[0])
                    print(f" (enum {field.enum}): {enum}")
                else:
                    print(": ", end='')
                    if field.length == 1: # if single value just print the value
                        print(f"{field.values[0]}")
                    else: # otherwise format as array
                        print(f"{field.values}")
            print()
    
    def validate_packet(self):
        # get packet id from name
        self.id = next((id for id, vals in config.boards["SE"].writes.items() if vals.get("name") == self.name), None)
        if self.id is None:
            warnings.warn(f"Error: Sequence Engine has no packet with name {self.name}")
            return False

        # find right packet for id
        packet_type = config.boards["SE"].writes.get(self.id)
        if packet_type is None:
            warnings.warn(f"Error: Sequence Engine has no packet with id {self.id}")
            return False
        
        # check destination board can read packet
        dest_packet = config.boards[self.board].reads.get(self.id)
        if dest_packet is None or dest_packet != packet_type:
            warnings.warn(f"Error: {self.board} cannot read packet type {packet_type}")
            return False
        
        # check data is formatted correctly
        for item in config.types[packet_type]:
            field = self.fields.get(item["symbol"])
            if field is None:
                warnings.warn(f"Error: missing field {item["symbol"]}")
                return False
            
            if "array" in item:
                length = item["array"]
                if not (isinstance(field, list) and len(field) == length):
                    warnings.warn(f"Error: field {field} is formatted incorrectly")
                    return False
                
            if "enum" in item:
                if not (field in config.types[item["enum"]].keys()):
                    warnings.warn(f"Error: {item["enum"]} has no key {field}")
                    return False
                
        return True

    # send packet
    # TO DO: SET UP ACTUAL SENDING CODE, THIS JUST BUILDS THE BYTEARRAY
    # ALSO HANDLE GD AND ABORT PACKET SENDING (SPECIAL CASES)
    def send(self):
        if not self.validate_packet():
            warnings.warn(f"Error: attempted to send invalid packet")
            return
        
        # the bytearray construction might be weird/messy but couldn't think of a different way
        # start by filling in data
        data_out = bytearray()

        packet_type = config.boards["SE"].writes.get(self.id)
        data_length = 0
        for item in config.types[packet_type]:
            format, length = get_data_format(item)
            byte_length = get_byte_length(format)
            data_length += byte_length
            data = self.fields[item["symbol"]]

            temp_out = bytearray(byte_length)
            if length == 1:
                if "enum" in item:
                    data = config.types[item["enum"]][data]

                struct.pack_into(format, temp_out, 0, data)
            else:
                bytes = int(byte_length / length)
                for i in range(length):
                    struct.pack_into(format[i], temp_out, i * bytes, data[i])

            data_out.extend(temp_out)

        header_format = "<BBIH"
        byte_length = get_byte_length(header_format)

        # pack the header (see parse_packet for format) and calculate checksum
        out = bytearray(byte_length)
        struct.pack_into(header_format, out, 0, self.id, data_length, 0, 0)

        checksum = fletcher16(out[:-2] + data_out)
        struct.pack_into("H", out, byte_length - 2, checksum)

        out.extend(data_out)
        return out

# -----------------------------------------------------
#
# Reading packets
#
# -----------------------------------------------------

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
    # packet data is formatted as
    # packet ID (uint8)
    # length of data (uint8)
    # time since board turned on (uint32)
    # checksum (uint16)
    # data (defined by packet spec)
    board_id = int(addr[0][-2:]) # last 2 digits of ip are board ID
    # format is based on byte size (ref. source above)
    unpack = struct.unpack_from("<BBIH", data[0:8])
    id = unpack[0] # from what i have seen id should be a str
    length = unpack[1]
    uptime = unpack[2]
    checksum = unpack[3]

    # add board name to packet
    if board_id not in config.id_to_board: # confirm packet board id
        warnings.warn(f"Warning: IP {addr[0]} not recognized")
        packet.error = True
        return packet
    
    board = config.boards[config.id_to_board[board_id]]
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
    if not id in board.writes:
        warnings.warn(f"Warning: Unrecognized packet {id} on {board}")
        packet.error = True
        return packet

    packet.name = board.writes[id]["name"]
    packet.fields = parse_data(field_data, board.writes[id])

    packet.error = False
    packet.print()

# returns struct format for packet item
def get_data_format(item):
    length = 1
    if "array" in item:
        length = item["array"]

    # parse byte array based on data type, ref struct lib
    match item["type"]:
        case "u8":
            format = "B" * length
        case "u16":
            format = "H" * length
        case "u32":
            format = "I" * length
        case "f32":
            format = "f" * length

    return format, length

# returns length (in bytes) of format string
def get_byte_length(format):
    byte_length = 0
    for c in format:
        # parse byte array based on data type, ref struct lib
        match c:
            case "B":
                byte_length += 1
            case "H":
                byte_length += 2
            case "I":
                byte_length += 4
            case "f":
                byte_length += 4

    return byte_length

# parse data field based on packet data type
def parse_data(data, type):
    fields = {}

    counter = 0
    for item in config.types[type]:
        field = PacketData()
        
        format, length = get_data_format(item)

        field.values = list(struct.unpack_from(format, data, counter))
        counter += get_byte_length(format)

        field.length = length

        if "enum" in item:
            field.enum = item["enum"]

        fields[item["symbol"]] = field

    return fields

# -----------------------------------------------------
#
# main loop (temp/debug)
#
# -----------------------------------------------------

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
# mc_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"Listening for UDP packets on port {BCAST_PORT}")

# while True:
#     # receive data
#     data, addr = mc_sock.recvfrom(1024)
#     parse_packet(data, addr)

