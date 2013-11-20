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

		#for now, these only define my state as a downloader (getting the file, not seeding the file)
		self.handshake = False 
		self.choked = True
		self.have = None
		self.interested = False
		#self.current_message = None
		self.bitfield = files.Bitfield(self.torrent)  #		 files.Bitfield(torrent).bitfield
		print "Initializing bitfield for peer %s: %r" % (self.id, self.bitfield.bitfield)
		self.requesting = False
		self.piece_so_far = 0
		self.subpiece = ''

	def connect(self):
		print "connecting to a peer..."
		self.socket.settimeout(120)
		self.socket.connect((self.ip, self.port))
		self.send_handshake()

	# If this Peer is our special "Client" peer, we're going to listen for incomming connections
	def listen(self):
		pass

	def isUnchoked(self):
		if self.choked == False and self.requesting == False:
			return True

		return False

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

	def recv_message(self):
		if self.handshake:
			print "Receiving message..."

			# First we expect to receive 4 bytes for the message length
			data = self.socket.recv(4)
			if data:
				length = int(unpack("!I", data)[0])
			else:
				# No data received, we are probably disconnected
				return False

			if length < 1:
				print "Message length < 1 - keepalive or invalid message."
				return False

			m = self.socket.recv(1)
			message_id = int(unpack('!B', m)[0])
			print "Received message of length %r and id %r" %(length, message_id)
			payload = None
			if length > 1:
				#basic messages have length 1, so the payload is whatever exceeds 1 byte (if any)
				if message_id == 7:
				 	payload = (self.socket.recv(4), self.socket.recv(4), self.socket.recv(length - 9))
				else:
					payload = self.socket.recv(length - 1)
				#print "Payload: ", payload
				self.react_to_message(message_id, payload)
			else:
				self.react_to_message(message_id)
		else:
			self.recv_handshake()

		return True

	def react_to_message(self, message_id, payload=None):
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
				#not sure what this one does, but I think it's where you sent the bitfield and the peer doesn't have the pieces you need, so drop the connection
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
				print "!!!!!!!!!!!!!!!!!!!!!!! GOT ONE PIECE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
				piece_index = unpack("!I", payload[0])[0]
				piece_begin = unpack("!I", payload[1])[0]
				print "Index: ", piece_index
				print "Begin: ", piece_begin
				print "Piece: ", payload[2]
				self.subpiece += payload[2]
				self.piece_so_far += len(self.subpiece)
				self.check_piece_completeness(piece_index)

			if message_id == mlist["cancel"]:
				print "Got cancel!"

			if message_id == mlist["port"]:
				print "Got port!"

			if message_id == 6:
				#request received and serve the piece requested, but handle this later
				pass

			if message_id == 7:
				#piece received, hash check and save to disk
				pass

	#first piece I need (is 0 in my_bitfield), if the peer also has it:
	def piece_to_request(self, bitfield_from_peer):
		print "Client bitfield: ", self.bitfield.bitfield
		print "Peer bitfield: ", bitfield_from_peer.bitfield
		for byte in range(0, len(self.bitfield.bitfield)):
			for bit in reversed(range(8)):				
				if ((int(self.bitfield.bitfield[byte]) >> bit) & 1) == 0:
					if ((int(bitfield_from_peer.bitfield[byte]) >> bit) & 1) == 1:
						return (8*byte + (7 - bit))
		# This peer doesn't have any of the pieces you need.
		
		return -1

	# Send peer a request for a new piece
	def send_piece_request(self, piece_index, begin=0):
		msg = messages.Request()
		send = msg.assemble(self.torrent, piece_index, begin)
		self.send_next_message(send)
		self.requesting = True
		self.unchoked = False

	def check_piece_completeness(self, piece_index):
		if self.piece_so_far < self.torrent.piece_length:
			self.send_piece_request(piece_index, self.piece_so_far)
			print "Piece is incomplete :("
		else:
			print "Piece is complete!", self.piece_so_far
			self.requesting = False
			self.unchoked = True
			Piece(self.torrent, piece_index, self.subpiece).check_piece_hash()
			self.piece_so_far = 0

	def send_next_message(self, assembled_message):	
		print "Sending message: ", assembled_message
		self.socket.sendall(assembled_message)

	# This lets the Peer class pretend to be a socket
	def fileno(self):
	    return self.socket.fileno()