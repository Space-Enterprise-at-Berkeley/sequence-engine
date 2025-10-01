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

# add host to multicast group, requires packing into ip_mreqn struct
# ref https://man7.org/linux/man-pages/man7/ip.7.html
mreq = struct.pack("=4s4s", mcast_group, host)  
mc_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

def read_packets_mc():
    data, addr = mc_sock.recvfrom(1024)
    packet = parse_packet(data, addr)
    PacketBuffer.update(packet)

def send_packet(packet):




    pass