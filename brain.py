from peer import Peer
from client import Client
import socket
from piece import Piece
import select
import random

class Brain(Peer):
    """A dispatcher with high-level powers that tells Clients what to do and can write to disk"""

    def __init__(self, peer_dict, torrent, tracker):
        self.tracker = tracker
        self.torrent = torrent
        Peer.__init__(self, peer_dict, torrent, peer_dict['id'])
        self.peers = []
        self.done = False
        # The piece dictionary is to make sure I don't make multiple requests for the same piece to different peers
        self.piece_dict = { i : None for i in range(self.torrent.no_of_subpieces)}

        # print "Peers from tracker: ", self.tracker.peers
        # print "Piece dictionary: ", self.piece_dict

    def add_peers(self):
        """Adds all the peers from the tracker to Peers list"""
        appended_peer = -1
        for peer_dict in self.tracker.peers:
            if peer_dict.get('id') != self.id:
                c = Client(peer_dict, self.torrent, self)
                self.peers.append(c)
                appended_peer += 1 

    def connect_all(self, n):
        """Takes a subset of peers from the Peers list and connects all of them together"""

        self.current_peers = random.sample(self.peers, n)
        # print "Current peers: %r" %[i.id for i in self.current_peers]
        for current_peer in self.current_peers:
            # print "Connecting to: %r" %current_peer.id
            current_peer.connect()

    def reconnect_all(self, n):
        """If all the current peers have been disconnected, connects to new ones from new socket"""

        self.current_peers = random.sample(self.peers, n)
        print "New current peers: %r" %[i.id for i in self.current_peers]
        for current_peer in self.current_peers:
            # print "Connecting to: %r" %current_peer.id
            current_peer.refresh_socket_and_connect()

    def is_complete(self):
        if self.bitfield.initialize_bitfield():
            return False
        else:
            return True

    def handle_piece(self, piece):
        """Verifies the piece that the Client sent over and sends it to be saved"""

        if piece.check_piece_hash:
            piece.write_to_disk()
            self.pieces_i_have += 1
            # Update the bitfield
            self.bitfield.update_bitfield(piece.index)
            if self.bitfield.bitfield == self.bitfield.complete_bitfield:
                # print "My bitfield %r = complete bitfield %r, looks like we have the whole file!" %(self.bitfield.bitfield, self.bitfield.complete_bitfield)
                piece.concatenate_pieces()
                self.complete = True
        else:
            print "Piece hash incorrect! Not a valid piece."

    def lock_this_piece(self, piece_index, client_id):
        """Puts the peer's ID as the value of the piece in the dictionary"""

        self.piece_dict[piece_index] = client_id

    def unlock_this_piece(self, piece_index):
        """Removes the peer's ID from the dictionary"""

        self.piece_dict[piece_index] = None

    def refresh_piece_dict(self):
        """In case any peer's ID got stuck in the dictionary and they never sent me the piece, reset it all"""

        self.piece_dict = { i : None for i in range(self.torrent.no_of_subpieces)}

    def run(self):
        """Runs the Clients and manages the connections"""

        while self.bitfield.bitfield != self.bitfield.complete_bitfield:

            # The fileno() function in the Peer class lets the peers pretend to be a socket
            ready_peers, ready_to_write, in_error = select.select(self.current_peers, [], [], 3)

            # print "...standby..."

            if self.complete:
                return False

            for p in ready_peers:
                # print p.id, "IS READY"
                status = p.process_messages()

            for p in self.current_peers:
                status = p.start_transfer()
                if status == False:
                    #If the file's done, stop
                    if self.complete:
                        return False
                    else:
                        print "Nothing left to download from peer %r." %p.id
                        self.current_peers.remove(p)
                        p.disconnect()
                        for peer in self.current_peers:
                            peer.send_keepalive()
                        # If I sent a piece request and it was never honored, remove this peer's ID from the pieces dictionary so the piece can be requested from someone else:
                        for index, peer in self.piece_dict.iteritems():
                            if peer == p.id:
                                self.piece_dict[index] = None
                        # print "Current peers: %r" %[i.id for i in self.current_peers]

            if not self.current_peers:
                print "Out of current peers, get new ones!"
                self.reconnect_all(3)
                self.refresh_piece_dict()
        
        
