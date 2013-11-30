import struct
import math
import hashlib
import piece
import glob
import os

class Bitfield(object):
	def __init__(self, torrent):
		self.total_length = torrent.total_length
		self.no_of_subpieces = int(torrent.no_of_subpieces)
		self.have_pieces = 0

		# self.complete = False
		self.torrent = torrent
		self.no_of_bytes = int(math.ceil(int(torrent.no_of_subpieces) / 8.0))
		self.bitfield = [0] * self.no_of_bytes
		self.complete_bitfield = self.complete_bitfield()
		# self.bitfield = self.initialize_bitfield()
	
	def set_bitfield_from_payload(self, payload):
		#print "Setting Bitfield from Payload: %r" % payload
		payload_unpacked = struct.unpack("!%dB" % (len(self.bitfield)), payload)
		#print "Payload unpacked: ", payload_unpacked
		for i in range(len(payload_unpacked)):
			self.bitfield[i] = payload_unpacked[i]
		print "Bitfield just set: %r" %self.bitfield

	def pack_bitfield(self):
		bitfield_list = [str(i) for i in self.bitfield]
		bitfield_string = ",".join(bitfield_list)
		bitfield_packed = struct.pack("%dB" % (len(self.bitfield)), *(i for i in self.bitfield))
		return bitfield_packed

	def update_bitfield(self, piece_index):
		#update the bitfield by changing the bit corresponding to the piece to a 1. This means, add the corresponding power of 2 to the byte containing that bit
		print "BITFIELD BEFORE UPDATE: %r" %self.bitfield
		byte_index = int(math.floor(piece_index / 8.0))
		self.bitfield[byte_index] += 2**(7 - (piece_index%8))
		print "Adding %r to this byte... " % (2**(7 - (piece_index%8)))
		print "BITFIELD AFTER UPDATE: %r" %self.bitfield

	def complete_bitfield(self):
		temp_list = [0] * self.no_of_bytes
		for i in range(self.torrent.no_of_subpieces):
			byte_index = int(math.floor(i / 8.0))
			temp_list[byte_index] += 2**(7 - (i%8))
		return temp_list

	def initialize_bitfield(self):
		# start with all zeroes like it is now
		# scan current directory (pieces.PATH), get a list of all files starting with torrent.name.00
		# for loop: take each element in the list, strip beginning "torrent.name.00" and what's left is the piece index that we have
					# call update_bitfield for each piece index
		# return bitfield list
		print "Scanning current directory and initializing bitfield..."
		os.chdir(piece.PATH)
		for files in glob.glob(self.torrent.name+".00*"):
			start = len(self.torrent.name)+3
			piece_index = int(files[start:])
			print "Piece index %r in directory: " % piece_index
			self.update_bitfield(piece_index)
		print "Done initializing bitfield from directory."




			
		