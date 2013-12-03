import bencode
from struct import *
import bitfield
import math

class Message(object):
    """Parent class for all messages in the protocol"""

    def __init__(self):
        self.prefix = "!IB"    

class Keepalive(Message):
    """Message of length 0, sent once every 2 min to prevent timeout"""

    def __init__(self):
        self.length  = 0

    def assemble(self):
        """Formats to send over the network"""
        self.m_id = None
        message = pack("!I", 0)
        return message

class Choke(Message):
    """Initial state of any connection. Fixed-length (0001), no payload"""

    def assemble(self):
        """Formats to send over the network"""
        self.m_id = 0
        message = pack(self.prefix, 1, self.m_id)
        return message

class Unchoke(Message):
    """Fixed length(0001), no payload"""

    def assemble(self):
        """Formats to send over the network"""

        self.m_id = 1
        message = pack(self.prefix, 1, self.m_id)
        return message

class Interested(Message):
    """Fixed length(0001), no payload"""
    
    def assemble(self):
        """Formats to send over the network"""  

        self.m_id = 2
        message = pack(self.prefix, 1, self.m_id)
        return message

class Not_interested(Message):
    "Fixed length(0001), no payload"""
    
    def assemble(self):
        """Formats to send over the network"""
        
        self.m_id = 3
        message = pack(self.prefix, 1, self.m_id)
        return message

class Have(Message):
    """Fixed length(0005), payload = 0-based index of a piece that was successfully downloaded and verified with hash"""
    
    def assemble(self, torrent, piece_index):
        """Formats to send over the network"""

        self.m_id = 4
        message = pack(self.prefix, 5, self.m_id, piece_index)
        return message

class BitMessage(Message):
    """Bitfield message - optional. May be sent by the downloader only right after handshake. Variable length"""

    def assemble(self, torrent):
        """Formats to send over the network"""

        self.m_id = 5
        bitfield_to_send = bitfield.Bitfield(torrent).pack_bitfield()
        bit_length = int(math.ceil(torrent.no_of_subpieces / 8.0))
        message = pack(self.prefix+'%ds' % bit_length, bit_length+1, self.m_id, bitfield_to_send)
        print "Bitfield assembled to send off: ", unpack("!IB%ds" % bit_length, message)
        return message

class Request(Message):
    """Fixed length(0013): <len=0013><id=6><index><begin><length>"""
    
    def assemble(self, torrent, piece_index, begin, block):
        """Formats to send over the network"""

        self.m_id = 6
        message = pack(self.prefix+"III", 13, 6, piece_index, begin, block)
        print "Request message: %r" % message
        return message

class Piece(Message):
    """Not implemented yet"""

    def assemble(self, torrent):
        self.m_id = 7

class Cancel(Message):
    """Not implemented yet"""

    def assemble(self):
        self.m_id = 8

class Port(Message):
    """Not implemented yet"""
    
    def assemble(self):   
        self.m_id = 9

