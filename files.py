import struct
import math
import hashlib

class Bitfield(object):
	def __init__(self, torrent):
		self.total_length = torrent.total_length
		self.no_of_subpieces = int(torrent.no_of_subpieces)
		self.have_pieces = 0
		self.complete = False
		self.torrent = torrent
		self.no_of_bytes = int(math.ceil(int(torrent.no_of_subpieces) / 8.0))
		self.bitfield = [0] * self.no_of_bytes

		# Make bitfield_packed a function not an attribute
	
	def set_bitfield_from_payload(self, payload):
		#print "Setting Bitfield from Payload: %r" % payload
		payload_unpacked = struct.unpack("!%dB" % (len(self.bitfield)), payload)
		#print "Payload unpacked: ", payload_unpacked
		self.bitfield = payload_unpacked

	def pack_bitfield(self):
		bitfield_list = [str(i) for i in self.bitfield]
		bitfield_string = ",".join(bitfield_list)
		bitfield_packed = struct.pack("%dB" % (len(self.bitfield)), *(i for i in self.bitfield))
		return bitfield_packed

	def update_bitfield(self, piece_index):
		#update the bitfield by changing the bit corresponding to the piece to a 1. This means, add the corresponding power of 2 to the byte containing that bit
		byte_index = int(math.ceil(piece_index / 8.0))
		if byte_index > 0:
			self.bitfield[byte_index - 1] += 2**(7 - (piece_index % 8))
		else:
			self.bitfield[byte_index] += 2**(7 - (piece_index % 8))
		