import socket
import messages
from struct import *
import files
from piece import Piece

class Peer(object):

	def __init__(self, peer_dict, torrent):
		#I will be a Peer instance too when I'm serving a file. We add a listening state
		self.ip = peer_dict['ip']
		self.port = peer_dict['port']
		self.id = peer_dict['id']
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.torrent = torrent

		self.handshake = False
		self.interested = False
		self.bitfield = files.Bitfield(self.torrent)
		print "Initializing bitfield for peer %s: %r" % (self.id, self.bitfield.bitfield) 

		#state machine:
		self.choked = True
		self.downloading = False
		self.requesting = False
		self.complete = False
		
		#these make up the buffer for incomplete messages:
		self.message_incomplete = False
		self.incomplete_data = ''
		self.incomplete_message_id = -1
		self.data_length = -1
		self.piece_data = ''
		self.have = -1

	def connect(self):
		print "connecting to a peer..."
		self.socket.settimeout(120)
		self.socket.connect((self.ip, self.port))
		self.send_handshake()

	# If this Peer is our special "Client" peer, we're going to listen for incomming connections
	def listen(self):
		pass

	def isUnchoked(self):
		if self.choked == False:
			return True
		return False

	def hasPiece(self):
		return self.have

	def send_handshake(self):
		#<pstrlen><pstr><reserved><info_hash><peer_id>
		pstr = 'BitTorrent protocol'
		handshake = pack("!B19s8x20s20s", len(pstr), pstr, self.torrent.info_hash, self.torrent.peer_id)
		print "[%s] sending handshake: %r" % (self.id, handshake)
		self.socket.send(handshake)

	def recv_handshake(self):
		re_handshake = self.socket.recv(1024)
		print re_handshake
		#verify info_hash
		reh_unpacked = unpack("!B19s8x20s20s", re_handshake)
		self.handshake = True

		print "Received handshake: ", reh_unpacked

	def get_entire_message(self):
		print "Buffer length before receiving 1 more segment %r" % len(self.incomplete_data)
		receiving = self.socket.recv(self.data_length - len(self.incomplete_data))
		print "Receing 1 segment of %r data..." %len(receiving)
		self.incomplete_data += receiving
		print "Buffer data length after receiving segment: ", len(self.incomplete_data)
		if len(self.incomplete_data) < self.data_length-1:
			self.recv_message()
			print "Received < block size. Calling Receive function again..."
		else:
			print "Received all. Message complete. Length of message: ", len(self.incomplete_data)
			self.react_to_message(self.incomplete_message_id, self.incomplete_data)
			self.message_incomplete = False
			self.incomplete_data = ''
			self.incomplete_message_id = -1
			self.data_length = -1

	def recv_message(self):
		if self.handshake:
			print "Receiving message..."

			#process incomplete messages:
			if self.message_incomplete:
				self.get_entire_message()

			else:
				# First we expect to receive 4 bytes for the message length
				self.data = self.socket.recv(4)
				if self.data:
					self.length = int(unpack("!I", self.data)[0])
				else:
					# No data received, we are probably disconnected
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

					print "Message length: ", self.length
					print "Actual length: ", actual_length

					if (actual_length != self.length-1):
						print "Received less than length. Sending to <get_entire_block> function..."
						self.incomplete_data+=payload
						self.data_length = self.length
						self.incomplete_message_id = message_id
						self.message_incomplete = True
						self.recv_message()

					else:
						self.react_to_message(message_id, payload)
		else:
			self.recv_handshake()

		return True

	def react_to_message(self, message_id, payload):
			mlist = {"keepalive":None, "choke": 0, "unchoke": 1, "interested":2, "not interested": 3, "have": 4, "bitfield": 5, "request": 6, "piece":7, "cancel": 8, "port": 9}
			#change state for all the above
			if message_id == mlist["keepalive"]:
				#keepalive - so ignore
				pass

			if message_id == mlist["choke"]:
				#choke received, what to do? send keepalives as usual and wait for unchoke
				print "Got choke!"
				self.choked = True
				pass

			if message_id == mlist["unchoke"]:
				#unchoke received, send request
				print "Got unchoke!"
				self.choked = False
#				request = messages.Request()
#				piece_index = files.Bitfield(self.torrent).piece_to_request(self.bitfield)
#				self.send_next_message(request.assemble(self.torrent, piece_index, 0), self.torrent)

			if message_id == mlist["interested"]:
				print "Got interested! "
				#interested received, handle this later because it's for seeding
				pass

			if message_id == mlist["not interested"]:
				print "Got not interested!"
				#for you sent the bitfield and the peer doesn't have the pieces you need, so drop the connection
				self.interested = False

			if message_id == mlist["have"]:
				print "Got have!"
				#have received, send interested
				self.interested = True
				interested = messages.Interested()
				self.send_next_message(interested.assemble())

			if message_id == mlist["bitfield"]:
				#print "Peer %s received bitfield: %r" % (self.id, payload)
				#bitfield received, send your own bitfield
				self.bitfield.set_bitfield_from_payload(payload)

				# This is temporary code to send a 0 bitfield to the client.  We will
				#   move this to the state machine in main_file
				bitfield_message = messages.BitMessage()
				self.send_next_message(bitfield_message.assemble(self.torrent))

			if message_id == mlist["piece"]:
				self.downloading = True
				print "!!!!!!!!!!!!!!!!!!!!!!! GOT ONE SUBPIECE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
				piece_index = unpack("!I", payload[0:4])[0]
				piece_begin = unpack("!I", payload[4:8])[0]
				self.piece_data += payload[8:]
				print "Piece index: ", piece_index
				print "Piece begin: ", piece_begin
				self.check_piece_completeness(piece_index)

			if message_id == mlist["cancel"]:
				print "Got cancel!"

			if message_id == mlist["port"]:
				print "Got port!"

			if message_id == mlist["request"]:
				#request received and serve the piece requested, but handle this later
				pass

	#first piece I need (is 0 in my_bitfield), if the peer also has it:
	def piece_to_request(self, bitfield_from_peer):
		for byte in range(0, len(self.bitfield.bitfield)):
			for bit in reversed(range(8)):				
				if ((int(self.bitfield.bitfield[byte]) >> bit) & 1) == 0:
					if ((int(bitfield_from_peer.bitfield[byte]) >> bit) & 1) == 1:
						return int((8*byte + (7 - bit)))
		# This peer doesn't have any of the pieces you need.	
		return -1

	# Send peer a request for a new piece
	def send_piece_request(self, piece_index, begin=0):
		msg = messages.Request()
		send = msg.assemble(self.torrent, piece_index, begin)
		self.send_next_message(send)
		self.requesting = True

	def check_piece_completeness(self, piece_index):
		if len(self.piece_data) < self.torrent.piece_length:
			print "Piece is incomplete, sending request for another block to begin at %r..." %len(self.piece_data)
			self.send_piece_request(piece_index, len(self.piece_data))
		else:
			print "Piece is complete! Length:", len(self.piece_data)
			self.write_piece(piece_index)	
			self.downloading = False
			self.requesting = False	
			
	def write_piece(self, piece_index):
		p = Piece(self.torrent, piece_index, self.piece_data)
		self.piece_data = ''
		if p.check_piece_hash:
			print "HASH MATCHES!"
			p.write_to_disk()
			self.have = piece_index
		else:
			print "Hash doesn't match. Not a valid piece!"
		print "Requesting next piece..."
		#self.send_piece_request(self.piece_to_request(self.bitfield))
			
	def send_next_message(self, assembled_message):	
		print "Sending message: %r" %assembled_message
		self.socket.sendall(assembled_message)

	# This lets the Peer class pretend to be a socket
	def fileno(self):
	    return self.socket.fileno()