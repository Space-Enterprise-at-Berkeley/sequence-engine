import socket, struct, sys, serial, argparse, warnings, time, threading
from packet import Packet, parse_packet
from packet_config import config
from serial.serialutil import SerialException

# ap = argparse.ArgumentParser(description="serial→Ethernet bridge (UDP)")
# ap.add_argument("-p", "--port", help="serial comport to use")
# ap.add_argument("-b", "--baud", default=230400)
# args = ap.parse_args()

# #find comport if not given
# if args.port is None:
#     import serial.tools.list_ports
#     ports = list(serial.tools.list_ports.comports())
#     if len(ports) == 0:
#         print("No serial ports found!")
#         sys.exit(1)
#     #look for one with serial in the description
#     for p in ports:
#         if "serial" in p.description.lower():
#             args.port = p.device
#             print(f"Using port {args.port} ({p.description})")
#             # if manufacturer is espressif, shift baud to 921600
#             if p.manufacturer and "espressif" in p.manufacturer.lower():
#                 args.baud = 921600
#                 print(f"Found Espressif device; setting baud to {args.baud}")
#                 args.port = p.device
#                 print(f"Using port {args.port} ({p.description} {args.baud})")
#             break
#     if args.port is None:
#         print("Did not find a USB Serial Device. Is one connected? Ports:")
#         for i, p in enumerate(ports):
#             print(f"{i}: {p.device} ({p.description})")
#         sel = int(input("Select port #: "))
#         args.port = ports[sel].device
#         print(f"Using port {args.port} ({ports[sel].description} {args.baud}) ")

# ser = serial.Serial(args.port, args.baud, timeout=3)
# ser.reset_input_buffer()
# ser.reset_output_buffer()
# serial_lock = threading.Lock()

# def write_serial_wrapped(data: bytes):
#     print(data)
#     """Write payload to serial wrapped with [[ and ]]. Thread-safe."""
#     try:
#         with serial_lock:
#             ser.write(b"[[")
#             ser.write(data)
#             ser.write(b"]]")
#             ser.flush()
#     except SerialException as e:
#         print(f"Serial write exception: {e}")

packet = Packet()
packet.name = "FCEnableRuncamPDB"
packet.board = "SE"
packet.fields = {
    "action": "ENABLE"
}

aaaa = bytearray([97, 100, 110, 97])
packet_data = packet.send(timebytes = aaaa)
# write_serial_wrapped(packet_data)
print(packet_data)
