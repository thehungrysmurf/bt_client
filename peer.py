import socket
import messages
from struct import *
import bitfield
from piece import Piece

class Peer(object):
    "A generic 'peer' - has Brain and Client as children and soon it'll have Server too"""

    def __init__(self, peer_dict, torrent, my_id):
        self.ip = peer_dict['ip']
        self.port = peer_dict['port']
        self.id = peer_dict.get('id') or peer_dict.get('peer id')
        if not self.id:
            print "No ID found. Not a valid peer."
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.torrent = torrent
        self.my_id = my_id

        self.bitfield = bitfield.Bitfield(self.torrent)
        self.bitfield.initialize_bitfield() 

        #State machine attributes:
        self.handshake = False
        self.choked = True
        self.downloading = False
        self.requesting = False
        self.complete = False
        self.connecting = False
        self.interested = False
        
        #Buffer variables for incomplete messages:
        self.message_incomplete = False
        self.incomplete_data = ''
        self.incomplete_message_id = -1
        self.data_length = -1
        self.piece_data = ''
        self.have = -1
        self.pieces_i_have = 0
        self.last_piece_index = (self.torrent.no_of_subpieces - 1)

    def connect(self):
        """Opens socket to connect to a peer"""

        print "Connecting to a peer...", self.id
        self.socket.settimeout(10)
        try:
            self.socket.connect((self.ip, self.port))
        except:
            return False
        self.send_handshake()
        self.connecting = True
        return True

    def disconnect(self):
        """Closes socket"""

        print "Disconnecting ---!"
        self.socket.close()
        self.connecting = False
        self.handshake = False

    def refresh_socket_and_connect(self):
        """Once the socket.close() function is called the socket can't be reused, so we have to create a new one and connect again"""
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Connecting to a peer from new socket...", self.id
        self.socket.settimeout(60)
        self.socket.connect((self.ip, self.port))
        self.send_handshake()
        self.connecting = True
        print "%r sending handshake after reconnect..." % self.id

    def is_unchoked(self):
        """Checks state of connection - once unchoked, I'm allowed to request pieces"""

        if self.choked == False:
                return True
        return False

    def send_handshake(self):
        """Initiates handshake. Format: <pstrlen><pstr><reserved><info_hash><peer_id>"""

        pstr = 'BitTorrent protocol'
        handshake = pack("!B19s8x20s20s", len(pstr), pstr, self.torrent.info_hash, self.my_id)
        print "%r sending handshake..." %self.id
        self.socket.send(handshake)

    def recv_handshake(self):
        """Receives and processes peer's handshake reply"""

        print "Receiving handshake from: ", self.id
        re_handshake = self.socket.recv(68)
        if len(re_handshake) > 68 or len(re_handshake) < 68:
            print "Expected handshake but received something else: ", re_handshake
            # self.recv_handshake()
        else:
            print "Handshake reply: %r" %re_handshake, len(re_handshake)
            # To add: verify info_hash
            reh_unpacked = unpack("!B19s8x20s20s", re_handshake)
            self.handshake = True
            self.interested = True
            interested = messages.Interested()
            self.send_next_message(interested.assemble())
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Received handshake from %r: %r" %(self.id, reh_unpacked)

    def get_entire_message(self):
        """Some messages arrive in separate TCP segments. I need a buffer to store the data until it reaches the length specified in the header"""

        # print "Buffer length before receiving 1 more segment %r" % len(self.incomplete_data)
        receiving = self.socket.recv(self.data_length - len(self.incomplete_data))
        # print "Receing 1 segment of %r data..." %len(receiving)
        self.incomplete_data += receiving
        # print "Buffer data length after receiving segment: ", len(self.incomplete_data)
        if len(self.incomplete_data) < self.data_length-1:
                self.recv_message()
                # print "Received < block size. Calling Receive function again..."
        else:
                # print "Received all. Message complete. Length of message: ", len(self.incomplete_data)
                self.react_to_message(self.incomplete_message_id, self.incomplete_data)
                self.message_incomplete = False
                print "Message complete! Processing message..."
                self.incomplete_data = ''
                self.incomplete_message_id = -1
                self.data_length = -1

    def recv_message(self):
        """First stop for receiving messages. Send them to process or keep them in the buffer if they're incomplete"""

        if self.handshake:
                print "Receiving message..."

                # Process incomplete messages:
                if self.message_incomplete:
                    self.get_entire_message()

                else:
                        # First we expect to receive 4 bytes for the message length
                        self.data = self.socket.recv(4)
                        if self.data:
                                self.length = int(unpack("!I", self.data)[0])
                        else:
                                # No data received, we're probably disconnected
                                return False

                        if self.length < 1:
                                print "Message length < 1 - keepalive or invalid message."
                                return False

                        m = self.socket.recv(1)
                        message_id = int(unpack('!B', m)[0])
                        print "Received message of length %r and id %r" %(self.length, message_id)
                        payload = None
                        if self.length == 1:
                                self.react_to_message(message_id, payload)
                        if self.length > 1:
                                #basic messages have length 1, so the payload is whatever exceeds 1 byte (if any)
                                if message_id == 7:
                                        print "Length from header: ", self.length                       
                                        i = self.socket.recv(4)
                                        index = str(unpack("!I", i)[0])
                                        b = self.socket.recv(4)
                                        begin = str(unpack("!I", b)[0])

                                        block = self.socket.recv(self.length - 9)
                                        payload = i+b+block
                                        actual_length = len(i)+len(b)+len(block)
                                
                                else:
                                        payload = self.socket.recv(self.length - 1)
                                        actual_length = len(payload)

                                if (actual_length != self.length-1):
                                        print "Received less than length. Sending to <get_entire_block> function..."
                                        self.incomplete_data+=payload
                                        self.data_length = self.length
                                        self.incomplete_message_id = message_id
                                        self.message_incomplete = True
                                        print "Message incomplete - waiting for entire message..."
                                        self.recv_message()

                                else:
                                        self.react_to_message(message_id, payload)
        else:
            # Can't send anything before handshake
            self.recv_handshake()

        return True

    def react_to_message(self, message_id, payload):
        """Process messages and respond accordingly"""

        mlist = {"keepalive":None, "choke": 0, "unchoke": 1, "interested":2, "not interested": 3, "have": 4, "bitfield": 5, "request": 6, "piece":7, "cancel": 8, "port": 9}

        if message_id == mlist["keepalive"]:
            # Keepalive - so ignore
            pass

        if message_id == mlist["choke"]:
            # Choke received, what to do? Send keepalives as usual and wait for unchoke
            print "Got 'Choke' message!"
            self.choked = True

        if message_id == mlist["unchoke"]:
            # Unchoke received, ready to send request
            print "Got 'Unchoke' message!"
            self.choked = False

        if message_id == mlist["interested"]:
            print "Got 'Interested' message! "
            # Interested received, handle this later because it's for seeding

        if message_id == mlist["not interested"]:
            print "Got 'Not Interested' message!"
            # If you sent the bitfield and the peer doesn't have the pieces you need - so drop the connection
            self.interested = False

        if message_id == mlist["have"]:
            print "Got 'Have' message, advertising piese of index %r!" %(unpack("!I", payload))[0]
            # Update bitfield for this peer with advertised piece
            self.bitfield.update_bitfield((unpack("!I", payload))[0])
            # Send Interested message back
            self.interested = True
            interested = messages.Interested()
            self.send_next_message(interested.assemble())

        if message_id == mlist["bitfield"]: 
            print "Got 'Bitfield' message!"
            self.bitfield.set_bitfield_from_payload(payload)
            # Send your own Bitfield and Interested
            bitfield_message = messages.BitMessage()
            self.send_next_message(bitfield_message.assemble(self.torrent))
            self.interested = True
            interested = messages.Interested()
            self.send_next_message(interested.assemble())

        if message_id == mlist["piece"]:
            self.downloading = True
            print "----------------------------------------------------------------GOT ONE SUBPIECE"
            piece_index = unpack("!I", payload[0:4])[0]
            piece_begin = unpack("!I", payload[4:8])[0]
            self.piece_data += payload[8:]
            print "Piece index: ", piece_index
            print "Piece begin: ", piece_begin
            if piece_index != self.last_piece_index:
                    self.check_piece_completeness(piece_index)
            else:
                    self.process_last_piece(piece_index)

        if message_id == mlist["cancel"]:
            print "Got 'Cancel' message!"

        if message_id == mlist["port"]:
            print "Got 'Port' message!"

        if message_id == mlist["request"]:
            print "Got 'Request' message!"
            # Serve the piece requested - work in progress

    def piece_to_request(self, bitfield_from_peer):
        """Compares my bitfield to the peer's bitfield and returns the first piece that I need (is 0 in my bitfield) if the peer also has it (is 1 in theirs)"""

        for byte in range(0, len(self.bitfield.bitfield)):
                for bit in reversed(range(8)):                          
                        if ((int(self.bitfield.bitfield[byte]) >> bit) & 1) == 0:
                            if ((int(bitfield_from_peer.bitfield[byte]) >> bit) & 1) == 1:
                                return int((8*byte + (7 - bit))) 
        return -1

    def send_piece_request(self, piece_index, block, begin=0):
        """Formats piece request message"""

        msg = messages.Request()
        send = msg.assemble(self.torrent, piece_index, begin, block)
        self.send_next_message(send)
        print "Sending a piece request for index %r..." %piece_index
        self.requesting = True

    def check_piece_completeness(self, piece_index):
        """Every time I get a piece message I check if I got the entire piece"""

        if len(self.piece_data) < self.torrent.piece_length:
            print "Piece is incomplete, sending request for another block to begin at %r..." %len(self.piece_data)
            self.send_piece_request(piece_index, self.torrent.block_size, len(self.piece_data))

        else:
            print "Piece is complete! Length:", len(self.piece_data)
            self.piece_complete(piece_index)
            self.downloading = False
            self.requesting = False     

    def piece_complete(self, piece_index):
        pass

    def file_complete(self):
        pass

    def process_last_piece(self, piece_index):
        """The last piece is a little different because it's of variable size""" 

        self.last_piece_size = self.torrent.total_length % self.torrent.piece_length
        print "This is the last piece, index %r , size %r" % (piece_index, self.last_piece_size)
        if len(self.piece_data) < self.last_piece_size:
            self.last_subpiece_length = self.last_piece_size % self.torrent.block_size
            self.send_piece_request(piece_index, self.last_subpiece_length, len(self.piece_data))

        else:
            print "Piece is complete! Length:", len(self.piece_data)
            self.piece_complete(piece_index)
            # self.file_complete()
            #self.write_piece(piece_index)   
            self.downloading = False
            self.requesting = False    
                        
    def write_piece(self, piece_index):
        """Now that the piece is complete, process and save it"""

        p = Piece(self.torrent, piece_index, self.piece_data)
        self.piece_data = ''
        if p.check_piece_hash:
            print "Hash matches!"
            p.write_to_disk()
            self.pieces_i_have += 1
            self.have = piece_index
        else:
            print "Hash doesn't match. Not a valid piece!"
                    
    def send_keepalive(self):
        """Just for testing right now"""

        print "Sending keepalive to %r" %self.id
        keepalive = messages.Keepalive()
        self.send_next_message(keepalive.assemble())

    def send_next_message(self, assembled_message):
        """Sends off assembled message"""

        print "Sending: %r" %assembled_message
        self.socket.sendall(assembled_message)

    def fileno(self):
        """This lets the Peer class pretend to be a socket"""
    
        return self.socket.fileno()