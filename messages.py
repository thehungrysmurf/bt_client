import bencode
import parse_torrent
from struct import *
#from connection import InitiateConnection

#introduce global variables that keep track of the steps that have been done - handshake happened, unchoke received, etc

def handshake(torrent):
    #<pstrlen><pstr><reserved><info_hash><peer_id>
    pstr = 'BitTorrent protocol'
    handshake = pack("!B19s8x20s20s", len(pstr), pstr, torrent.info_hash, torrent.peer_id)
    return handshake

def assemble_message(message_name):
    prefix = "!IB"
    message_types = {"keepalive":None, "choke": 0, "unchoke": 1, "interested":2, "not interested": 3, "have": 4, "bitfield": 5, "request": 6, "piece":7, "cancel": 8, "port": 9}
    if message_name == "interested":
        message = pack(prefix, 1, message_types[message_name])
    if message_name == "bitfield":
        what_i_have = pack('B', int('00000000'))
        bitfield = what_i_have*7
        message = pack(prefix+'7s', 17, message_types[message_name], bitfield)
    if message_name == "request":
        #request very first piece, no offset, block = 2^14
        message = pack(prefix+"III", 13, 6, 0, 0, 16384)
    if message_name == "unchoke":
        message = pack(prefix, 1, message_types[message_name])
    return message

def get_message_type(connection):
    l = connection.receive_message(4)
    if len(l) < 1:
        return "Message length < 1 - keepalive or invalid message."
    length = int(unpack("!I", l)[0])
    m = connection.receive_message(1)
    message_id = unpack("!B", m)[0]
    if length > 1:
        payload = connection.receive_message(length-1)
    return length, message_id, payload

class Message(object):
    #alternatively, create a dictionary like Zach: Messages = {'keepalive': -1, 'choke':0, 'unchoke':1, ....}
    def __init__():
        self.prefix = "!I"

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

class bitfield(Message):
    #may be sent by the downloader only immediately after handshake is completed & before sending anything else
    #variable length
    #doesn't have to be sent if the downloader has no pieces
    m_id = 5

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

