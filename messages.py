import bencode
from struct import *
import bitfield
import math

class Message(object):
    def __init__(self):
        self.prefix = "!IB"    

    # def recv(self, socket, length):
    #     # Subtrack 1 from length for message_id
    #     self.length = length
    #     payload = socket.recv(self.length-1)
    #     return payload

class Keepalive(Message):
    #messages of length 0, sent once every 2 min to prevent timeout
    def __init__(self):
        self.length  = 0
    def assemble(self):
        self.m_id = None

class Choke(Message):
    #initial state of any connection
    #fixed-length (0001), no payload
    def assemble(self):
        self.m_id = 0
        message = pack(self.prefix, 1, self.m_id)
        return message

class Unchoke(Message):
    #official BT client has an algorithm for doing this. At any one time only one peer gets unchoked. Which peer gets unchoked rotates every 30 sec
    #fixed length(0001), no payload
    def assemble(self):
        self.m_id = 1
        message = pack(self.prefix, 1, self.m_id)
        return message

class Interested(Message):
    #fixed length(0001), no payload
    def assemble(self):
        self.m_id = 2
        message = pack(self.prefix, 1, self.m_id)
        return message

class Not_interested(Message):
    #fixed length(0001), no payload
    def assemble(self):
        self.m_id = 3
        message = pack(self.prefix, 1, self.m_id)
        return message

class Have(Message):
    #fixed length(0005), payload = zero-based index of a piece that was successfully downloaded and verified with hash
    def assemble(self, torrent, piece_index):
        self.m_id = 4
        message = pack(self.prefix, 5, self.m_id, piece_index)
        return message

class BitMessage(Message):
#     #may be sent by the downloader only immediately after handshake is completed & before sending anything else
#     #variable length
    def assemble(self, torrent):
        self.m_id = 5
        bitfield_to_send = bitfield.Bitfield(torrent).pack_bitfield()
        print "Length of bitfield payload: ", len(bitfield_to_send)
        # message = pack(self.prefix+'15s', len(bitfield_to_send)+1, self.m_id, bitfield_to_send)
        # print "Bitfield Assemble: ", unpack("!IB15s", message)
        bit_length = int(math.ceil(torrent.no_of_subpieces / 8.0))
        message = pack(self.prefix+'%ds' % bit_length, bit_length+1, self.m_id, bitfield_to_send)
        print "Bitfield assembled: ", unpack("!IB%ds" % bit_length, message)
        return message

class Request(Message):
    #fixed length(0013)
    #<len=0013><id=6><index><begin><length>
    def assemble(self, torrent, piece_index, begin, block):
        #request very first piece, no offset, block = 2^14
        self.m_id = 6
        message = pack(self.prefix+"III", 13, 6, piece_index, begin, block)
        print "Request message: %r" % message
        return message

class Piece(Message):
    def assemble(self, torrent):
        self.m_id = 7
        #ELABORATE HERE

class Cancel(Message):
    def assemble(self):
        self.m_id = 8

class Port(Message):
    def assemble(self):
        self.m_id = 9

