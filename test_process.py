import bencode
import requests
import hashlib
from struct import pack, unpack
from torrent import Torrent
from connection import InitiateConnection
import messages
import select
import sys

TORRENT_TEST_FILE = '/home/silvia/Hackbright/my_BT_client/misc/torrents/File_1.torrent'

def main():
    t = Torrent(TORRENT_TEST_FILE)
    print "************Metainfo: ", t.info_dict
    #print "************Piece length: ", t.piece_length
    #print "************No. of subpieces", t.no_of_subpieces
    #print "************List of hashes of subpieces: ", t.list_of_subpieces_hashes
    #print "************Info hash: ", t.info_hash.encode('base64')
    c = InitiateConnection('10.1.10.167', 51413)
    #print "************Response from tracker to HTTP GET request: ", c.send_request_to_tracker(t)
    handshake = messages.handshake(t)
    #print "************Sending handshake: ", handshake
    c.connect_to_peer()
    c.send_message(handshake)
    received = c.receive_message(1024)
    received_unpacked = unpack("!B19s8x20s20s", received)
    print "************Full response handshake from peer: ", received
    #print "************Response handshake from peer unpacked: ", received_unpacked
    #print "************Peer id from peer: ", received[-20:]
    #print "************Info hash from peer: ", hashlib.sha1(received_unpacked[2]).hexdigest()
    #print "************Info hash from peer: ", received_unpacked[2].encode('base64')

    inputs = [c.s]
    running = True
    list_of_messages = []

    # #sending bitfield:
    # b = messages.assemble_message("bitfield")
    # print "sending bitfield: ", unpack("!IB7s", b)
    # c.send_message(b)
    # rb = messages.get_message_type(c)
    # print messages.get_message_type(c)

    # sending interested:
    i = messages.assemble_message("interested")
    print "sending interested: ", unpack("!IB", i)
    c.send_message(i)
    #print "reply: ", messages.get_message_type(c)

    while running:
            ready_to_read, ready_to_write, in_error = select.select(inputs, [], [])
            for i in ready_to_read:
                print "receving message"
                msg = i.recv(4)

                # length = i.recv(4)
                # m_id = i.recv(1)
                # if length > 1:
                #     msg = i.recv(length-1)
                sys.stdout.write(msg)
                list_of_messages.append(msg)
                # msg = ''
                # while len(msg) < MSGLEN:
                #    chunk = self.s_receive.recv(MSGLEN-len(msg))
                #    msg = msg + chunk
    
    """print "reply: ", rb
    print "size of payload: ", len(rb[2])
    print "payload: %r" %rb[2]
    unpacked_payload = unpack("!7B", rb[2])
    print "payload unpacked: ", unpacked_payload"""


    
    #sending unchoke:
    u = messages.assemble_message("unchoke")
    print "sending unchoke: ", unpack("!IB", u)
    c.send_message(u)
    # ru = messages.get_message_type(c)
    # print "reply: ", ru

    """#sending request:
    req = messages.assemble_message("request")
    print "sending request: ", unpack("!IBIII", req)
    c.send_message(req)
    rr = messages.get_message_type(c)
    print "reply: ", rr"""

if __name__ == "__main__":
    main()
