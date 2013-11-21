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
		if hashlib.sha1(self.data).digest() == self.torrent.list_of_subpieces_hashes[self.index]:
			#self.have_pieces += 1
			#update_bitfield(self.index)
			return True
		else:
			print "Piece hash incorrect! Not a valid piece."
			return False

	def write_to_disk(self):
		print "WRITING PIECE TO DISK..."
		self.parent_path = '//home/silvia/Downloads/silvia_bt/'
		self.piece_file_name = self.parent_path+self.torrent.name+'.'+'00'+str(self.index)
		print "piece file name: ", self.piece_file_name
		piece_file = open(self.piece_file_name, 'w+')
		piece_file.write(self.data)
		piece_file.close()

		#self.piece_file = open("")