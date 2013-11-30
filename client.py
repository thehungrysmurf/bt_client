from peer import Peer
import socket
from piece import Piece

class Client(Peer):
    def __init__(self, peer_dict, torrent, brain):
        Peer.__init__(self, peer_dict, torrent)
        self.brain = brain

    @property
    def transferring(self):
        return self.requesting & self.downloading

    def run(self):
        next_piece = -1
        """Returns true if we still have stuff to do and need to be run again, returns false if we're dead"""
        if not self.recv_message(): # Potentially, a message is a piece
            self.socket.close()
            return False

        if self.brain.complete:
            return False

        if self.choked:
            return True

        print "Peer %s is unchoked!" % self.id
        print "Peer %s's Bitfield: %r" % (self.id, self.bitfield.bitfield)
        print "My bitfield: %r" %self.brain.bitfield.bitfield 
        print "Complete bitfield: %r" %self.brain.bitfield.complete_bitfield

        print "TRANSFERRING? ", self.transferring

        if not self.transferring:
            if not self.choked:
                next_piece = self.brain.piece_to_request(self.bitfield)

                if next_piece >= 0: # we've been told to get a new piece
                    print "Next piece to request: ", next_piece
                    if not self.brain.piece_dict.get(next_piece):
                        print "^^^^^^^^^^^^^^^^ Piece is unlocked, do your thing ^^^^^^^^^^^^^^^^^"
                        print "PIECE DICTIONARY: %r" %self.brain.piece_dict
                        self.brain.lock_this_piece(next_piece, self.id)
                        self.send_piece_request(next_piece, self.torrent.block_size)
                    else:
                        print "//////////////// Piece is locked, get the next one ////////////////"
                        print "PIECE DICTIONARY: %r" %self.brain.piece_dict

                else:
                    print "No next piece :-("
                    # self.socket.close()
                    return False

        return True

    def piece_complete(self, piece_index): # Callback when piece has downloaded
        # send the piece to the brain
        p = Piece(self.torrent, piece_index, self.piece_data)
        self.brain.handle_piece(p)
        self.brain.unlock_this_piece(piece_index) 
        self.piece_data = ''

    def file_complete(self):
        self.brain.complete = True

# critical section - the locked part of the program where threads need the RLock to enter
# what's my critical section? Writing? Requesting? The whole Request / Receive process?