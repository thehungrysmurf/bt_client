import bencode
import requests
import hashlib
from struct import pack, unpack
from torrent import Torrent
from connection import InitiateConnection

TORRENT_TEST_FILE = '/home/silvia/Hackbright/my_BT_client/misc/torrents/File_1.torrent'

def main():
    t = Torrent(TORRENT_TEST_FILE)
    #print "************Metainfo: ", t.info_dict
    print "************Piece length: ", t.piece_length
    print "************No. of subpieces", t.no_of_subpieces
    print "************List of hashes of subpieces: ", t.list_of_subpieces_hashes
    print "************Info hash: ", t.info_hash_readable
    c = InitiateConnection('192.168.1.6', 6881)
    print "************Response from tracker to HTTP GET request: ", c.send_request_to_tracker(t) 
    handshake = c.generate_handshake_to_peer(t)
    print "************Sending handshake: ", handshake
    c.connect_to_peer()
    c.send_message(handshake)
    received = c.receive_message(handshake)
    print "************Full response handshake from peer: ", received
    print "************Peer id from peer: ", received[-20:]
    print "************Info hash from peer: ", hashlib.sha1(received[-40:-20]).hexdigest()
    prefix = "!IB"
    interested_message = pack(prefix, 1, 2)
    c.send_message(interested_message)
    reply_to_interested = c.receive_message(interested_message)
    print "Reply to interested: ", unpack("!IB", reply_to_interested)

if __name__ == "__main__":
    main()