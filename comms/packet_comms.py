from comms.packet_config import config
from comms.packet import *
from comms.packet_buffer import PacketBuffer

import socket, struct

ENGINE_IP = "10.0.0.177" # CHANGE WHEN MOVING TO PI

BCAST_PORT = 42099
MCAST_PORT = 42080

#define ips
host = socket.inet_aton(f"10.0.0.{sys.argv[1]}")
mcast_group = socket.inet_aton("224.0.0.3")

# create broadcast UDP socket
bc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
bc_sock.bind(("", BCAST_PORT))

# create multicast UDP socket
mc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
mc_sock.bind(("", MCAST_PORT))

mono_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# add host to multicast group, requires packing into ip_mreqn struct
# ref https://man7.org/linux/man-pages/man7/ip.7.html
mreq = struct.pack("=4s4s", mcast_group, host)  
mc_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

def read_packets_mc():
    data, addr = mc_sock.recvfrom(1024)
    packet = parse_packet(data, addr)
    PacketBuffer.update(packet)

def send_packet(packet, data):

    if packet.name == "Abort": # send aborts over broadcast
        bc_sock.sendall(data)

    elif packet.board == "GD": # send dashboard packets over multicast
        mc_sock.sendall(data)
    
    else: # monocast to a specific board, given by packet.board
        ip = f"10.0.0.{config.board_to_id[packet.board]}"
        try:
            mono_sock.connect((ENGINE_IP, BCAST_PORT))
            mono_sock.sendall(data)
        except Exception as e:
            print(f"Sequence engine could not connect to {packet.board}:{ip}")
            mono_sock.close()

            mono_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            

    pass