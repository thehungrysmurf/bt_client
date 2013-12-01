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
        self.piece_dict = { i : None for i in range(self.torrent.no_of_subpieces)}

        print "PEERS FROM TRACKER: ", self.tracker.peers
        print "PIECE DICTIONARY: ", self.piece_dict

    def add_peers(self):
        appended_peer = -1
        for peer_dict in self.tracker.peers:
            if peer_dict['id'] != self.id:
                c = Client(peer_dict, self.torrent, self)
                self.peers.append(c)
                appended_peer += 1 
                print "Length of peer list: ", len(self.peers)

    def connect_all(self, n):
        self.current_peers = random.sample(self.peers, n)
        print "Current peers: %r" %[i.id for i in self.current_peers]
        for current_peer in self.current_peers:
            print "Connecting to: %r" %current_peer.id
            current_peer.connect()

    def reconnect_all(self, n):
        self.current_peers = random.sample(self.peers, n)
        print "New current peers: %r" %[i.id for i in self.current_peers]
        for current_peer in self.current_peers:
            print "Connecting to: %r" %current_peer.id
            current_peer.refresh_socket_and_connect()

    def handle_piece(self, piece):
        if piece.check_piece_hash:
            piece.write_to_disk()
            self.pieces_i_have += 1
            # update the bitfield
            self.bitfield.update_bitfield(piece.index)
            if self.bitfield.bitfield == self.bitfield.complete_bitfield:
                print "My bitfield %r = complete bitfield %r, looks like we have the whole file!" %(self.bitfield.bitfield, self.bitfield.complete_bitfield)
                piece.concatenate_pieces()
                self.complete = True
                print "TORRENT COMPLETE!"
        else:
            print "Hash suxxxx" 

    def lock_this_piece(self, piece_index, client_id):
        self.piece_dict[piece_index] = client_id

    def unlock_this_piece(self, piece_index):
        self.piece_dict[piece_index] = None

    def refresh_piece_dict(self):
        self.piece_dict = { i : None for i in range(self.torrent.no_of_subpieces)}

    def run(self):
        # running = True
        # while running:
        while self.bitfield.bitfield != self.bitfield.complete_bitfield:
            ready_peers, ready_to_write, in_error = select.select(self.current_peers, [], [], 3)
            # print [p.id for p in ready_peers], "ARE READY"

            print "...standby..."

            for p in ready_peers:
                print p.id, "IS READY"
                status = p.run()

                """Done with this peer"""
                if status == False:
                    """If the file's done too, kill it"""
                    if self.complete:
                        return False
                    else:
                        print "Nothing left to download from peer %r." %p.id
                        self.current_peers.remove(p)
                        p.disconnect()
                        # if I sent a request and it was never honored, remove this peer's ID from the pieces dictionary:
                        for index, peer in self.piece_dict.iteritems():
                            if peer == p.id:
                                self.piece_dict[index] = None
                                # print "Removed peer's ID from pieces dictionary: %r" %self.piece_dict
                        print "Current peers: %r" %[i.id for i in self.current_peers]

                if not self.current_peers:
                    print "No more current peers, get new ones!"
                    self.reconnect_all(3)
                    self.refresh_piece_dict()

                    if self.complete:
                        print "GROOVY! You successfully downloaded a torrent."
                        return False
                        # running = False
        
        