import socket, struct, sys, serial, argparse, warnings

if __name__ == "__main__":
    BCAST_PORT = 42099
    MCAST_PORT = 42080

    ap = argparse.ArgumentParser(description="serial→Ethernet bridge (UDP)")
    ap.add_argument("--port", required=True)
    ap.add_argument("--debug", action="store_true")

    args = ap.parse_args()

    #define ips
    mono_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

else:
    from comms.packet_comms import *

# Serial
ser = serial.Serial(args.port, baudrate=921600, timeout=3)
ser.reset_input_buffer()
ser.reset_output_buffer()

def read_exactly(n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = ser.read(n - len(buf))
        if not chunk:
            warnings.warn("Serial timeout (>3 seconds) while reading")
            return
        buf += chunk
    return bytes(buf)

def sync_to_start():
    # find b'[['
    got_open = 0
    while True:
        b = ser.read(1)
        if not b:
            warnings.warn("Serial timeout (>3 seconds) waiting for start '[['")
            return False
        if b == b'[':
            got_open += 1
            if got_open == 2:
                return True
        else:
            got_open = 0

def read_one_packet() -> list[int]:
    # 1) sync to start
    if not sync_to_start():
        return

    # 2) read header: id(1), len(1), timestamp(4), checksum(2)  => 8 bytes
    hdr = read_exactly(8)
    if hdr is None:
        return
    pkt_id, pkt_len = hdr[0], hdr[1]

    # basic sanity
    if pkt_len > 256:
        warnings.warn(f"bad length {pkt_len}")
        return

    # 3) read payload + trailer
    body = read_exactly(pkt_len + 2)          # data + ']]'
    data   = body[:pkt_len]
    trailer = body[pkt_len:]
    if trailer != b']]':
        warnings.warn(f"bad trailer {trailer!r}")
        return

    # Return inner packet in the same layout verify_packet expects:
    # [id, len, ts0..3, csum0, csum1, data...]
    # packet_bytes = list(hdr[:6]) + list(hdr[6:8]) + list(data)
    packet_bytes = bytearray(hdr[:6]) + bytearray(hdr[6:8] + bytearray(data))

    print("received and successfully parsed packet:")
    print(packet_bytes)

    return packet_bytes

# -----------------------------------------------------
#
# Debug loop, uncomment and call with --debug flag
#
# -----------------------------------------------------

addr = "10.0.0.67"

# main loop, read packet bytes, remove delimiters, send over ethernet
while 1:
    try:
        packet = read_one_packet()
        if packet is None:
            print(f"Failed to read packet; trying again")
            continue
        packet = len(addr).to_bytes(1, "little") + addr.encode() + packet
        if args.debug:
            print("sending packet to loopback")
            print(f"bytes sent: {mono_sock.sendto(packet, ("127.0.0.1", BCAST_PORT))}")
            print()
    except ValueError as e:
        warnings.warn(e)

