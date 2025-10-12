import warnings

from comms.packet import Packet
from comms.packet_config import config

class PacketBuffer:
    MAX_BUFFER_SIZE = 10

    buffer = {}
    iterators = {} # need a position iterator for each packet type

    def __init__(self):
        for board in config.boards.values():
            PacketBuffer.buffer[board.name] = {}
            PacketBuffer.iterators[board.name] = {}

    def print():
        for board, packets in PacketBuffer.buffer.items():
            print("-------------------------------")
            print(f"{board}:")
            for id, packet in packets.items():
                it = PacketBuffer.iterators[board][id]
                packet[it].print()
            print("-------------------------------")

    # prints 'num' most recent (up to PacketBuffer.MAX_BUFFER_SIZE) packets of specified type
    def print_packet(board: str, id: int, num=1):
        try:
            it = PacketBuffer.iterators[board][id]
        except KeyError:
            warnings.warn(f"Error: board name or packet id does not exist")
            return
        
        if num > PacketBuffer.MAX_BUFFER_SIZE:
            warnings.warn(f"requested number is greater than buffer size, printing {PacketBuffer.MAX_BUFFER_SIZE}")
            num = 10

        for i in range(num):
            packet = PacketBuffer.buffer[board][id][(it + i) % PacketBuffer.MAX_BUFFER_SIZE]
            packet.print()

    def update(packet):
        iterator = 0
        if packet.id in PacketBuffer.iterators[packet.board]:
            iterator = PacketBuffer.iterators[packet.board][packet.id]

            # iterate iterator (ring buffer)
            if iterator == PacketBuffer.MAX_BUFFER_SIZE:
                PacketBuffer.iterators[packet.board][packet.id] = 0
            else:
                PacketBuffer.iterators[packet.board][packet.id] += 1
                
        else: # create new iterator & buffer for packet
            PacketBuffer.iterators[packet.board][packet.id] = 0
            PacketBuffer.buffer[packet.board][packet.id] = []

        PacketBuffer.buffer[packet.board][packet.id][iterator] = packet

packet_buffer = PacketBuffer()