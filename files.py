from torrent import Torrent
import struct
import math
import hashlib

class Bitfield(object):
	def __init__(self, torrent):
		self.total_length = torrent.total_length
		self.no_of_subpieces = int(torrent.no_of_subpieces)
		self.have_pieces = 0
		self.complete = False
		self.no_of_bytes = int(math.ceil(int(torrent.no_of_subpieces) / 8.0))
		self.my_bitfield = [0] * self.no_of_bytes
		self.bitfield_packed = struct.pack("%db" % (len(self.my_bitfield)), *(i for i in self.my_bitfield))

	def update_my_bitfield(self, piece_index):
		#update the bitfield by changing the bit corresponding to the piece to a 1. This means, add the corresponding power of 2 to the byte containing that bit
		byte_index = int(math.ceil(piece_index / 8.0))
		if byte_index > 0:
			self.my_bitfield[byte_index - 1] += 2**(7 - (piece_index % 8))
		else:
			self.my_bitfield[byte_index] += 2**(7 - (piece_index % 8))
	
	def check_piece_hash(self, piece, piece_index):
		if hashlib.sha1(piece) == torrent.list_of_subpieces_hashes[piece_index]:
			self.have_pieces += 1
			update_my_bitfield(piece_index)
			return True
		else:
			print "Piece hash incorrect! Not a valid piece."
			return False

	def first_piece_i_need(self):
		for byte in range(len(self.my_bitfield)):
			for bit in reversed(range(8)):
				if ((int(self.my_bitfield[byte]) >> bit) & 1) == 0:
					print "The first piece I need is located at byte %r and index %r = position %r overall" %(byte, bit, (8*byte + (7 - bit)))
					return (8*byte + (7 - bit))

	def first_piece_that_peer_has(self, bitfield_from_peer):
		for byte in range(len(bitfield_from_peer)):
			for bit in reversed(range(8)):
				if ((int(bitfield_from_peer[byte]) >> bit) & 1) == 1:
					print "The first piece the peer has is located at byte %r and index %r = position %r overall" %(byte, bit, (8*byte + (7 - bit)))
					return (8*byte + (7 - bit))
		