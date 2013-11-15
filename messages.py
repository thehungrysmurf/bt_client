import bencode
import parse_torrent
from struct import *
#from connection import InitiateConnection

#introduce global variables that keep track of the steps that have been done - handshake happened, unchoke received, etc

#**********TO DO:
#CREATE 'SEND_MESSAGE' METHOD, TAKES A MESSAGE CLASS TYPE AS A PARAMETER
#IN MAIN FILE, SET A CONNECTION CLASS (OR A MESSAGE CLASS?) TO BE THE 'OUTPUTS' - DON'T FORGET THE 'FILENO' FUNCTION!
#HAVE A HUGE 'IF' STATEMENT IN THE OUTPUTS SECTION OF THE SELECT WHERE SENDING MESSAGE DEPENDING ON STATE OF PEER: EX. IF HANDSHAKE EXCHANGED, SEND MESSAGE(BITFIELD) / IF BITFIELD RECEIVED, SEND MESSAGE(INTERESTED)

def assemble_message(message_name):
    prefix = "!IB"
    message_types = {"keepalive":None, "choke": 0, "unchoke": 1, "interested":2, "not interested": 3, "have": 4, "bitfield": 5, "request": 6, "piece":7, "cancel": 8, "port": 9}
    if message_name == "interested":
        message = pack(prefix, 1, message_types[message_name])
    if message_name == "bitfield":
        what_i_have = pack('15b', 0,0,1,0,1,0,0,0,0,0,0,0,0,0,0)
        bitfield = what_i_have*7
        message = pack(prefix+'15s', 16, message_types[message_name], bitfield)
    if message_name == "request":
        #request very first piece, no offset, block = 2^14
        message = pack(prefix+"III", 13, 6, 0, 0, 16384)
    if message_name == "unchoke":
        message = pack(prefix, 1, message_types[message_name])
    return message

def create_send_message(message_type):
    if message_type isinstance Interested:
        message = pack(prefix, 1, message_type.m_id)
    if message_type isinstance Bitfield:
        #CALCULATE YOUR BITFIELD HERE:
        what_i_have = pack('15b', 0,0,1,0,1,0,0,0,0,0,0,0,0,0,0)
        bitfield = what_i_have*7
        message = pack(prefix+'15s', 16, message_type.m_id, bitfield)
    if message_type isinstance Request:
        #right now requesting very first piece, no offset, block = 2^14. 
        #CALCULATE WHAT PIECE TO GET BASED ON PEER'S BITFIELD/HAVE AND YOUR BITFIELD
        message = pack(prefix+"III", 13, 6, 0, 0, 16384)
    if message_type isinstance Unchoke:
        message = pack(prefix, 1, message_type.m_id)

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

class Bitfield(Message):
    #may be sent by the downloader only immediately after handshake is completed & before sending anything else
    #variable length
    #doesn't have to be sent if the downloader has no pieces
    m_id = 5
    payload = None

    def recvBitfield(self, socket):
        self.payload = self.recv(socket)

    def getBitfield(self):
        pass

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

