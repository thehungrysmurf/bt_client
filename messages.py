import bencode
from struct import *
import files

def assemble_message(message_id, torrent):
    prefix = "!IB"
    message_types = {"keepalive":None, "choke": 0, "unchoke": 1, "interested":2, "not interested": 3, "have": 4, "bitfield": 5, "request": 6, "piece":7, "cancel": 8, "port": 9}
    if message_id == 2:
        message = pack(prefix, 1, message_id)
    if message_id == 5:
        b = files.Bitfield(torrent)
        bitfield_to_send = b.bitfield_packed
        message = pack(prefix+'15s', 16, message_id, bitfield_to_send)
        print "Bitfield Assemble: ", unpack("!IB15s", message)
    if message_id == 6:
        #request very first piece, no offset, block = 2^14
        message = pack(prefix+"III", 13, 6, 0, 0, 16384)
    if message_id == 1:
        message = pack(prefix, 1, message_id)
    return message

class Message(object):
    #alternatively, create a dictionary like Zach: Messages = {'keepalive': -1, 'choke':0, 'unchoke':1, ....}
    def __init__(self, length):
        self.prefix = "!I"
        self.length = length

    def recv(self, socket):
        # Subtrack 1 from length for message_id
        payload = socket.recv(self.length-1)

        return payload

class keepalive(Message):
    #messages of length 0, sent once every 2 min to prevent timeout
    #len = 0000
    m_id = None

class choke(Message):
    #the initial state of any connection
    #means the peer is not sending you the file until they "unchoke" you
    #fixed-length (0001), no payload
    m_id = 0

class unchoke(Message):
    #official BT client has an algorithm for doing this. At any one time only one peer gets unchoked. Which peer gets unchoked rotates every 30 sec
    #fixed length(0001), no payload
    m_id = 1

class interested(Message):
    #client sends to mean = "I want to download this file from you"
    #fixed length(0001), no payload
    m_id = 2

class not_interested(Message):
    #fixed length(0001), no payload
    m_id = 3

class have(Message):
    #fixed length(0005), payload = zero-based index of a piece that was successfully downloaded and verified with hash
    m_id = 4

# class Bitfield(Message):
#     #may be sent by the downloader only immediately after handshake is completed & before sending anything else
#     #variable length
#     #doesn't have to be sent if the downloader has no pieces
#     m_id = 5
#     payload = None

#     def recvBitfield(self, socket):
#         self.payload = self.recv(socket)

#     def getBitfield(self):
#         pass

class request(Message):
    #fixed length(0013)
    #<len=0013><id=6><index><begin><length>
    m_id = 6

class piece(Message):
    m_id = 7

class cancel(Message):
    m_id = 8

class port(Message):
    m_id = 9

