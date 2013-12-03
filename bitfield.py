import struct
import math
import hashlib
import piece
import glob
import os

class Bitfield(object):
	"""Keeps track of which pieces I have and which I need"""

	def __init__(self, torrent):
		self.torrent = torrent
		self.total_length = torrent.total_length
		self.no_of_subpieces = int(torrent.no_of_subpieces)
		self.no_of_bytes = int(math.ceil(int(torrent.no_of_subpieces) / 8.0))
		self.bitfield = [0] * self.no_of_bytes
		self.complete_bitfield = self.complete_bitfield()
	
	def set_bitfield_from_payload(self, payload):
		"""Initializes a peer's bitfield from a received Bitfield message"""

		payload_unpacked = struct.unpack("!%dB" % (len(self.bitfield)), payload)
		for i in range(len(payload_unpacked)):
			self.bitfield[i] = payload_unpacked[i]
		print "Bitfield set from payload: %r" %self.bitfield

	def pack_bitfield(self):
		"""Packs my bitfield to send to a peer"""

		bitfield_list = [str(i) for i in self.bitfield]
		bitfield_string = ",".join(bitfield_list)
		bitfield_packed = struct.pack("%dB" % (len(self.bitfield)), *(i for i in self.bitfield))
		return bitfield_packed

	def update_bitfield(self, piece_index):
		"""Updates the bitfield by changing the bit corresponding to the piece to a 1. This means, add the corresponding power of 2 to the byte containing that bit"""

		print "Bitfield before update: %r" %self.bitfield
		byte_index = int(math.floor(piece_index / 8.0))
		self.bitfield[byte_index] += 2**(7 - (piece_index%8))
		print "Adding %r to this byte... " % (2**(7 - (piece_index%8)))
		print "Bitfield after update: %r" %self.bitfield

	def complete_bitfield(self):
		"""Calculates the complete bitfield"""

		temp_list = [0] * self.no_of_bytes
		for i in range(self.torrent.no_of_subpieces):
			byte_index = int(math.floor(i / 8.0))
			temp_list[byte_index] += 2**(7 - (i%8))
		return temp_list

	def initialize_bitfield(self):
		"""Scans current directory and initializes bitfield with any pieces that are in there"""

		print "Scanning current directory, initializing bitfield..."
		if os.path.exists(os.path.join(piece.PATH,self.torrent.name)):
			self.bitfield = self.complete_bitfield
			print "I have the entire file."
		else:
			for files in glob.glob(os.path.join(piece.PATH, self.torrent.name+".00*")):
				root, ext = os.path.splitext(files)
				piece_index = int(ext[1:])
				print "Piece index %r in directory." %piece_index
				self.update_bitfield(piece_index)
		print "Done initializing bitfield from directory."




			
		