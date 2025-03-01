import socket
import struct
import sys

# under construction, parse packet data
def parsePacket(data, addr):

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
    print(f"Received multicast packet from {addr[0]}:{addr[1]}: " + data.hex(" ") + '\n')