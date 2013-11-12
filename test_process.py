import bencode
import requests
import hashlib
from struct import pack, unpack
from torrent import Torrent
from connection import InitiateConnection

TORRENT_TEST_FILE = '/home/user/silvia/my_torrents_as_tracker/file_1.torrent'

def main():
    t = Torrent(TORRENT_TEST_FILE)
    print "************Metainfo: ", t.info_dict
    print "************Piece length: ", t.piece_length
    print "************No. of subpieces", t.no_of_subpieces
    #print "************List of hashes of subpieces: ", t.list_of_subpieces_hashes
    print "************Info hash: ", t.info_hash_readable
    c = InitiateConnection('10.1.10.25', 51413)
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
    print "************Info hash from peer: ", hashlib.sha1(received_unpacked[2]).hexdigest()
    prefix = "!IB"
    interested_message = pack(prefix, 1, 2)
    c.send_message(interested_message)
    size_of_message = int(unpack("!I", c.receive_message(4))[0])
    message_id = c.receive_message(1)
    if ((size_of_message - 1) > 0):
        payload = c.receive_message(size_of_message - 1)
    print "Size of message: %r" %size_of_message
    print "Message id: ", unpack("!B", message_id)[0]
    print "Payload: %r" %payload
    print "Payload unpacked: ", unpack("!7B", payload)

if __name__ == "__main__":
    main()
