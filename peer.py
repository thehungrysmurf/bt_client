import socket
import messages
from struct import *

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
		self.bitfield = False
		self.request = False
	
	def connect(self):
		print "connecting to a peer..."
		self.socket.settimeout(120)
		self.socket.connect((self.ip, self.port))
		self.send_handshake()

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
				payload = self.socket.recv(length - 1)
				print "Payload: ", len(payload), payload
			self.react_to_message(message_id)

		else:
			self.recv_handshake()

		return True

	def react_to_message(self, message_id):
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
				self.send_next_message(mlist["request"], self.torrent)

			if message_id == mlist["interested"]:
				print "Got interested! "
				#interested received, handle this later because it's for seeding
				pass

			if message_id == mlist["not interested"]:
				print "Got not interested!"
				#not sure what this one does, but I think it's where you sent the bitfield and the peer doesn't have the pieces they need, so drop the connection
				self.interested = False

			if message_id == mlist["have"]:
				print "Got have!"
				#have received, send interested
				self.interested = True
				self.send_next_message(mlist["interested"], self.torrent)

			if message_id == mlist["bitfield"]:
				print "Got bitfield!"
				#bitfield received, send your own bitfield
				self.bitfield = True
				#self.send_next_message(message_id)
				self.send_next_message(mlist["bitfield"], self.torrent)

			if message_id == mlist["piece"]:
				print "Got piece!"

			if message_id == mlist["cancel"]:
				print "Got cancel!"

			if message_id == mlist["port"]:
				print "Got port!"

			# else:
			# 	print "Got something else!"

			# 	if length >= 1:
			# 		self.current_message.recvBitfield(self.socket)
			# 		self.bitfield = self.current_message.getBitfield()

			# 		# (for now) send empty bitfield.  This will need to come from our peer once we make one
			# 		#self.send_test_bitfield()

			# 		self.current_message = None

				# Process bitfield message

			if message_id == 6:
				#request received and serve the piece requested, but handle this later
				pass

			if message_id == 7:
				#piece received, save to disk (seek)
				pass

	def send_next_message(self, message_id, torrent):	
		send = messages.assemble_message(message_id, torrent)
		print "Sending message with id %r: %r" %(message_id, send)
		self.socket.sendall(send)

	# Pass along the peer's fileno() refernce.
	# This lets the Peer class pretend to be a socket
	def fileno(self):
	    return self.socket.fileno()