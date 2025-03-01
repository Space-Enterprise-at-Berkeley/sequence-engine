import socket
import sys

if len(sys.argv) < 2:
    print("Missing IP argument")
    sys.exit()

#UDP_IP = "127.0.0.1"
UDP_PORT = 42099
print(sys.argv[1])
host = socket.inet_aton(f"10.0.0.{sys.argv[1]}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.bind(("", UDP_PORT))

print(f"Listening for UDP packets on port {UDP_PORT}")

while True:
    # receive data
    data, addr = sock.recvfrom(1024)
    print(f"Received packet from {addr}: {data.decode('utf-8')}")