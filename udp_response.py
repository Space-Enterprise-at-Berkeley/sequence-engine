import socket
import struct
import sys
import json

if len(sys.argv) < 2:
    print("Missing IP argument")
    sys.exit()

#UDP_IP = "127.0.0.1"
BCAST_PORT = 42099
MCAST_PORT = 42080

host = socket.inet_aton(f"10.0.0.{sys.argv[1]}")
group = socket.inet_aton("224.0.0.3")

bc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
bc_sock.bind(("", BCAST_PORT))

mc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
mc_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 128)
mc_sock.bind(("", MCAST_PORT))
mreq = struct.pack("=4s4s", group, host)
mc_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"Listening for UDP packets on port {BCAST_PORT}")

#while True:
    # receive data
    # data, addr = bc_sock.recvfrom(1024)
    # print(f"Received broadcast packet from {addr}: {data.decode('utf-8')}")
    # print("bobr")

data, addr = mc_sock.recvfrom(1024)
print(json.loads(data))
    # print(f"Received multicast socket from {addr}: {data.decode('utf-8')}")