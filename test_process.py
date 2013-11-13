import bencode
import requests
import hashlib
from struct import pack, unpack
from torrent import Torrent
from connection import InitiateConnection
import messages

TORRENT_TEST_FILE = '/home/silvia/Hackbright/my_BT_client/misc/torrents/File_1.torrent'

def main():
    t = Torrent(TORRENT_TEST_FILE)
    print "************Metainfo: ", t.info_dict
    print "************Piece length: ", t.piece_length
    print "************No. of subpieces", t.no_of_subpieces
    #print "************List of hashes of subpieces: ", t.list_of_subpieces_hashes
    print "************Info hash: ", t.info_hash.encode('base64')
    c = InitiateConnection('127.0.0.1', 51413)
    print "************Response from tracker to HTTP GET request: ", c.send_request_to_tracker(t)
    handshake = c.generate_handshake_to_peer(t)
    print "************Sending handshake: ", handshake
    c.connect_to_peer()
    c.send_message(handshake)
    received = c.receive_message(1024)
    received_unpacked = unpack("!B19s8x20s20s", received)
    print "************Full response handshake from peer: ", received
    print "************Response handshake from peer unpacked: ", received_unpacked
    print "************Peer id from peer: ", received[-20:]
    #print "************Info hash from peer: ", hashlib.sha1(received_unpacked[2]).hexdigest()
    print "************Info hash from peer: ", received_unpacked[2].encode('base64')
    interested_message = messages.assemble_message(2)
    c.send_message(interested_message)
    size_of_interested_message = int(unpack("!I", c.receive_message(4))[0])
    
    message_id = c.receive_message(1)
    
    if ((size_of_interested_message - 1) > 0):
        payload = c.receive_message(size_of_interested_message - 1)
    print "Size of interested message: %r" %size_of_interested_message
    print "Message id: ", unpack("!B", message_id)[0]
    print "Size of payload: ", len(payload)
    print "Payload: %r" %payload
    unpacked_payload = unpack("!15B", payload)
    print "Payload unpacked: ", unpacked_payload
    bitfield = messages.assemble_message(5)
    print "bitfield: ", bitfield
    c.send_message(bitfield)
    x = c.receive_message(1024)
    print x


    """request_message = pack("!IBIII", 13, 6, 0, 0, 16384)
    c.send_message(request_message)
    x = c.receive_message(1024)
    print unpack('!IB', x)
    print len(x)"""

if __name__ == "__main__":
    main()
