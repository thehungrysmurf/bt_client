from peer import Peer
import socket
from piece import Piece
import select

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

    def connect_all(self):
        appended_peer = -1
        for peer_dict in self.tracker.peers:
            if peer_dict['id'] != self.id:
                c = Client(peer_dict, self.torrent, self)
                self.peers.append(c)
                appended_peer += 1 
                print "Length of peer list: ", len(self.peers)
                self.peers[appended_peer].connect()
                print "CONNECTING TOOOOOO ", self.peers[appended_peer].id

    def handle_piece(self, piece):
        if piece.check_piece_hash:
            piece.write_to_disk()
            self.pieces_i_have += 1

            # update our bitfield
            self.bitfield.update_bitfield(piece.index)
        else:
            print "Hash suxxxx" 

    def run(self):
        running = True
        while running:
            ready_peers, ready_to_write, in_error = select.select(self.peers, [], [], 3)
            print [p.id for p in ready_peers], "ARE READY"

            print "...select returned..."

            for p in ready_peers:
                print p.id, "IS READY"
                status = p.run()

                """Done with this peer"""
                if status == False:
                    self.peers.remove(p)

                    if self.complete:
                        print "GROOVY! You successfully downloaded a torrent."
                        running = False
        
        

class Client(Peer):
    def __init__(self, peer_dict, torrent, brain):
        Peer.__init__(self, peer_dict, torrent)
        self.brain = brain

    @property
    def transferring(self):
        return self.requesting

    def run(self):
        next_piece = -1
        """Returns true if we still have stuff to do and need to be run again, returns false if we're dead"""
        if not self.recv_message(): # Potentially, a message is a piece
            self.socket.close()
            return False

        if self.choked:
            return True

        print "Peer %s is unchoked!" % self.id
        print "Peer %s's Bitfield: %r" % (self.id, self.bitfield.bitfield)

        if not self.transferring:
            if not self.choked:
                next_piece = self.brain.piece_to_request(self.bitfield)

                if next_piece >= 0: # we've been told to get a new piece
                    print "Next piece to request: ", next_piece
                    self.send_piece_request(next_piece, self.torrent.block_size)

                else:
                    print "File is complete! No pieces left to download."
                    self.socket.close()
                    return False

        return True

    def piece_complete(self, piece_index): # Callback when piece has downloaded
        # send the piece to the brain
        p = Piece(self.torrent, piece_index, self.piece_data)
        self.brain.handle_piece(p) 
        self.piece_data = ''

    def file_complete(self):
        self.brain.complete = True