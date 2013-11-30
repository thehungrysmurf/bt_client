from peer import Peer
from client import Client
import socket
from piece import Piece
import select
import random

class Brain(Peer): # peer??? maybe???
    def __init__(self, peer_dict, torrent, tracker):
        self.tracker = tracker
        self.torrent = torrent
        #super(Peer, self).__init__(tracker, torrent)
        Peer.__init__(self, peer_dict, torrent)
        self.peers = []
        self.done = False

        print "PEERS FROM TRACKER: ", self.tracker.peers

    def connect_all(self):
        print "length of peer list: ", len(self.peers)

    def connect_all(self, n):
        appended_peer = -1
        for peer_dict in self.tracker.peers:
            if peer_dict['id'] != self.id:
                c = Client(peer_dict, self.torrent, self)
                self.peers.append(c)
                appended_peer += 1 
                print "Length of peer list: ", len(self.peers)
            print "ONE PEER IN PEER LIST: ", peer_dict['id']
        self.current_peers = random.sample(self.peers, n)
        for current_peer in self.current_peers:
            current_peer.connect()
            print "1 CURRENT PEER: ", current_peer.id

    def handle_piece(self, piece):
        if piece.check_piece_hash:
            piece.write_to_disk()
            self.pieces_i_have += 1
            # update the bitfield
            self.bitfield.update_bitfield(piece.index)
            if self.bitfield.bitfield == self.bitfield.complete_bitfield:
                print "My bitfield %r = complete bitfield %r, putting file together..." %(self.bitfield.bitfield, self.bitfield.comple)
                piece.concatenate_pieces()
                self.complete = True
        else:
            print "Hash suxxxx" 

    def run(self):
        running = True
        while running:
            ready_peers, ready_to_write, in_error = select.select(self.current_peers, [], [], 3)
            print [p.id for p in ready_peers], "ARE READY"

            print "...select returned..."

            for p in ready_peers:
                print p.id, "IS READY"
                status = p.run()

                """Done with this peer"""
                if status == False:
                    print "Nothing left to download from this peer."
                    self.current_peers.remove(p)

                if not self.current_peers:
                    self.connect_all(3)

                    if self.complete:
                        print "GROOVY! You successfully downloaded a torrent."
                        running = False
        
        