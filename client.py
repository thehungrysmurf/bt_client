from peer import Peer
import socket
from piece import Piece

class Client(Peer):
    """A pawn of the Brain, does the low-level tasks and waits for instructions from the Brain"""

    def __init__(self, peer_dict, torrent, brain):
        Peer.__init__(self, peer_dict, torrent, brain.my_id)
        self.brain = brain

    @property
    def transferring(self):
        return self.requesting

    def process_messages(self):
        """Returns true if we still have stuff to do and need to be run again, returns false if we're dead"""

        # print "(((((((((((((((((((((((( CLIENT %r IS RUNNING ))))))))))))))))))))))))" %self.id
        
        if not self.recv_message():
            self.socket.close()
            return False

        return True

    def start_transfer(self):
        """Sends piece requests for pieces the Brains tells it about"""

        if self.brain.complete:
            return False

        if self.choked:
            return True

        # print "Peer %s is unchoked!" % self.id
        # print "Peer %s's Bitfield: %r" % (self.id, self.bitfield.bitfield)
        # print "My bitfield: %r" %self.brain.bitfield.bitfield 

        # Valid piece indices start at 0
        next_piece = -1

        if not self.transferring:
            if not self.choked:
                next_piece = self.brain.piece_to_request(self.bitfield)

                # Brain told me to get a new piece
                if next_piece >= 0: 
                    # print "Next piece to request: ", next_piece
                    if not self.brain.piece_dict.get(next_piece):
                        # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Piece is UNLOCKED, do your thing."
                        self.brain.lock_this_piece(next_piece, self.id)
                        self.send_piece_request(next_piece, self.torrent.block_size)
                    # else:
                    #     print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Piece is LOCKED by %r, get the next one." %self.brain.piece_dict.get(next_piece)

                else:
                    # print "No next piece :-("
                    return False

        return True

    def piece_complete(self, piece_index):
        """Sends the complete piece to the brain"""

        p = Piece(self.torrent, piece_index, self.piece_data)
        self.brain.handle_piece(p)
        self.brain.unlock_this_piece(piece_index) 
        self.piece_data = ''

    def file_complete(self):
        """When I have the whole file"""

        self.brain.complete = True