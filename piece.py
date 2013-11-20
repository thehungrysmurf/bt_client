import hashlib

class Piece(object):
	def __init__(self, torrent, index, data):
		self.index = index
		self.torrent = torrent
		self.hash_check = self.torrent.list_of_subpieces_hashes[index]
		self.length_check = self.torrent.piece_length
		self.complete = False
		self.length = 0
		self.data = data

	def check_piece_hash(self):
		if hashlib.sha1(self.data) == self.torrent.list_of_subpieces_hashes[self.index]:
			self.have_pieces += 1
			update_bitfield(self.index)
			self.write_to_disk()
			return True
		else:
			print "Piece hash incorrect! Not a valid piece."
			return False

	def write_to_disk(self):
		print "Writing to disk..."