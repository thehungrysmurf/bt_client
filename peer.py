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

		self.handshake = False 
		self.choked = True
		self.interested = False
		#self.current_message = None
		self.bitfield = None
	
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
			l = self.socket.recv(4)
			if len(l) < 1:
				return "Message length < 1 - keepalive or invalid message."
			length = int(unpack("!I", l)[0])
			print "length: ", length
			m = self.socket.recv(1)
			print "id: ", unpack("!B", m)[0]
			message_id = unpack("!B", m)[0]
			payload = None
			if length > 1:
				payload = self.socket.recv(length-1)
				print "Payload: ", len(payload)

			# if message_id == 5:
			# 	self.current_message = messages.Bitfield(length)

			# 	if length >= 1:
			# 		self.current_message.recvBitfield(self.socket)
			# 		self.bitfield = self.current_message.getBitfield()

			# 		# (for now) send empty bitfield.  This will need to come from our peer once we make one
			# 		#self.send_test_bitfield()

			# 		self.current_message = None

				# Process bitfield message

		else:
			self.recv_handshake()

	# Pass along the server's fileno() refernce.
	# This lets the Client class pretend to be a socket
	def fileno(self):
	    return self.socket.fileno()