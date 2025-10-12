import socket, struct, sys, serial, argparse, warnings, time

if __name__ == "__main__":
    from packet import Packet
    from packet_config import config
    
    BCAST_PORT = 42099
    MCAST_PORT = 42080

    ap = argparse.ArgumentParser(description="serial→Ethernet bridge (UDP)")
    ap.add_argument("-p", "--port", required=True)
    ap.add_argument("-i", "--id", help="the id of the FC board", required=True)
    ap.add_argument("-b", "--baud", default=921600)
    ap.add_argument("-d", "--debug", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")

    args = ap.parse_args()

    #define ips
    mono_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

else:
    from comms.packet_comms import *
    from comms.packet_config import config
    from comms.packet import Packet

# ip address of FC
fc_id = config.board_to_id["FC_1"]
addr=f"10.0.0.{fc_id}"

# initialize rate variables
bps = 0 # bytes per second
pps = 0 # packets per second
err_count = 0 # packet error count
timeouts = 0 # timeout counter

# Serial
ser = serial.Serial(args.port, args.baud, timeout=3)
ser.reset_input_buffer()
ser.reset_output_buffer()

def read_exactly(n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = ser.read(n - len(buf))
        bps += len(chunk) # add chunk to byte counter
        if not chunk:
            warnings.warn("Serial timeout (>3 seconds) while reading")
            timeouts += 1
            return
        buf += chunk
    return bytes(buf)

def sync_to_start():
    # find b'[['
    got_open = 0
    while True:
        b = ser.read(1)
        bps += len(b) # add byte to counter
        if not b:
            warnings.warn("Serial timeout (>3 seconds) waiting for start '[['")
            timeouts += 1
            bps -= 1
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
    bps += len(hdr)

    if hdr is None:
        bps -= 8
        return
    pkt_id, pkt_len = hdr[0], hdr[1]

    # basic sanity
    if pkt_len > 256:
        warnings.warn(f"bad length {pkt_len}")
        err_count += 1
        return

    # 3) read payload + trailer
    body = read_exactly(pkt_len + 2)          # data + ']]'
    bps += len(body) # add bytes to counter

    data   = body[:pkt_len]
    trailer = body[pkt_len:]
    if trailer != b']]':
        warnings.warn(f"bad trailer {trailer!r}")
        err_count += 1
        return

    # Return inner packet in the same layout verify_packet expects:
    # [id, len, ts0..3, csum0, csum1, data...]
    # packet_bytes = list(hdr[:6]) + list(hdr[6:8]) + list(data)
    packet_bytes = bytearray(hdr[:6]) + bytearray(hdr[6:8] + bytearray(data))

    if args.verbose:
        print("received and successfully parsed packet:")
        packet = parse_packet(packet_bytes, addr)
        packet.print()
    else:
        print("received and successfully parsed packet:")
        print(packet_bytes)
    pps += 1

    return packet_bytes

def send_debug_packet():
    packet = Packet()
    packet.name = "DummyRates"
    packet.board = fc_id
    packet.fields = {
        "byteRate": bps,
        "packetRate": pps,
        "errorCount": err_count,
        "timeoutCount": timeouts
    }
    packet.send()

# -----------------------------------------------------
#
# Debug loop, uncomment and call with --debug flag
#
# -----------------------------------------------------

prevTime = 0
secondCounter = 0

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

    if args.verbose:
        send_debug_packet()
        print("------------------------")
        print(f"{bps} bytes per second | {pps} packets per second | {err_count} malformed packets | {timeouts} timeouts")
        print("------------------------")
        secondCounter += time.time() - prevTime
        if secondCounter >= 1:
            bps = 0
            pps = 0
            secondCounter = 0
