import socket, struct, sys, serial, argparse, warnings, time, threading
from packet import Packet, parse_packet
from packet_config import config
from serial.serialutil import SerialException

packet = Packet()
packet.name = "FCEnableBaroCalibration"
packet.board = "SE"
packet.fields = {
    "action": "ENABLE"
}

aaaa = bytearray([120, 120, 120, 77])
packet_data = packet.send(timebytes = aaaa)
print(packet_data)

ap = argparse.ArgumentParser(description="serial→Ethernet bridge (UDP)")
ap.add_argument("-s", "--send", action="store_true")
ap.add_argument("-p", "--port", help="serial comport to use")
ap.add_argument("-b", "--baud", default=115200)
args = ap.parse_args()

if args.send:
    #find comport if not given
    if args.port is None:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        if len(ports) == 0:
            print("No serial ports found!")
            sys.exit(1)
        #look for one with serial in the description
        for p in ports:
            if "serial" in p.description.lower():
                args.port = p.device
                print(f"Using port {args.port} ({p.description})")
                # if manufacturer is espressif, shift baud to 921600
                if p.manufacturer and "espressif" in p.manufacturer.lower():
                    args.baud = 115200
                    print(f"Found Espressif device; setting baud to {args.baud}")
                    args.port = p.device
                    print(f"Using port {args.port} ({p.description} {args.baud})")
                break
        if args.port is None:
            print("Did not find a USB Serial Device. Is one connected? Ports:")
            for i, p in enumerate(ports):
                print(f"{i}: {p.device} ({p.description})")
            sel = int(input("Select port #: "))
            args.port = ports[sel].device
            print(f"Using port {args.port} ({ports[sel].description} {args.baud}) ")

    ser = serial.Serial(args.port, args.baud, timeout=3)
    print(ser)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    serial_lock = threading.Lock()

    def write_serial_wrapped(data: bytes):
        print(data)
        """Write payload to serial wrapped with [[ and ]]. Thread-safe."""
        try:
            with serial_lock:
                ser.write(b"[[")
                ser.write(data)
                ser.write(b"]]")
                ser.flush()
        except SerialException as e:
            print(f"Serial write exception: {e}")

    # initialize rate variables
    bps = 0 # bytes per second
    pps = 0 # packets per second
    err_count = 0 # packet error count
    timeouts = 0 # timeout counter
    last_time = bytearray(4) # for adding matching timestamps to debug packets
    
    def sync_to_start():
        global bps, timeouts
        # find b'[['
        got_open = 0
        while True:
            b = ser.read(1)
            bps += len(b) # add byte to counter
            if not b:
                print("Serial timeout (>3 seconds) waiting for start '[['")
                timeouts += 1
                return False
            if b == b'[':
                got_open += 1
                if got_open == 2:
                    return True
            else:
                got_open = 0

    def read_exactly(n: int) -> bytes:
        global bps, timeouts

        buf = bytearray()
        while len(buf) < n:
            chunk = ser.read(n - len(buf))
            bps += len(chunk) # add chunk to byte counter
            if not chunk:
                print("Serial timeout (>3 seconds) while reading")
                timeouts += 1
                return
            buf += chunk
        return bytes(buf)

    def read_one_packet() -> list[int]:
        global bps, err_count, pps, last_time

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
            print(f"bad length {pkt_len}")
            err_count += 1
            return

        # 3) read payload + trailer
        body = read_exactly(pkt_len + 2)          # data + ']]'

        data   = body[:pkt_len]
        trailer = body[pkt_len:]
        if trailer != b']]':
            print(f"bad trailer {trailer!r}")
            err_count += 1
            return

        # Return inner packet in the same layout verify_packet expects:
        # [id, len, ts0..3, csum0, csum1, data...]
        # packet_bytes = list(hdr[:6]) + list(hdr[6:8]) + list(data)
        packet_bytes = bytearray(hdr[:6]) + bytearray(hdr[6:8] + bytearray(data))
        last_time = hdr[2:6]

        if hdr[0] == 12:
            print(f"received and successfully parsed packet:")
            packet = parse_packet(packet_bytes, ["10.0.0.81"])
            packet.print()
        pps += 1

        return packet_bytes

    write_serial_wrapped(packet_data)
    time.sleep(2.5)
    log = str(ser.read_all())
    log = log.split('Runcam: ')
    for bit in log:
        print(bit[:100])

    
    error = False
while 1:
    try:
        if error:
            print("Attempting to resync...")
            ser.close()
            time.sleep(1)
            ser.open()
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            error = False
            
        packet = read_one_packet()
        if packet is None:
            print(f"Failed to read packet; trying again")
            continue

    except ValueError as e:
        print(e)
    except SerialException as e:
        print(f"Serial exception: {e}")
        error = True
