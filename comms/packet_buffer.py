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
            for packet in packets.values():
                packet.print()

            print("-------------------------------")

    def update(packet):
        iterator = 0
        if packet.id in PacketBuffer.iterators[packet.board]:
            PacketBuffer.iterators[packet.board][packet.id] += 1
            iterator = PacketBuffer.iterators[packet.board][packet.id]
        else:
            PacketBuffer.iterators[packet.board][packet.id] = 0
            PacketBuffer.buffer[packet.board][packet.id] = []
        
        #iterator = 

        #PacketBuffer.buffer[packet.board][packet.id]

packet_buffer = PacketBuffer()