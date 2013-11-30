import hashlib
from glob import iglob
import shutil
import os
import re

PATH = '/home/s/Downloads/silvia_bt/'

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
		print "--------------------------------------------------------WRITING PIECE %r TO DISK" %self.index
		self.piece_file_name = PATH+self.torrent.name+'.'+'00'+str(self.index)
		print "piece file name: ", self.piece_file_name
		piece_file = open(self.piece_file_name, 'w')
		piece_file.write(self.data)
		piece_file.close()
		# if self.index == self.torrent.no_of_subpieces-1:
		# 	self.concatenate_pieces()
	
	def sort_numbers(self, value):
		numbers = re.compile(r'(\d+)')
		parts = numbers.split(value)
		parts[1::2] = map(int, parts[1::2])
		return parts

	def concatenate_pieces(self):
		print "Concatenating pieces into final file..."
		self.final_file_name = PATH+self.torrent.name
		self.destination = open(self.final_file_name, 'wb')
		# print "Destination: ", self.destination
		# with open(self.final_file_name, "ab") as myfile:
		# 	for i in range(self.torrent.no_of_subpieces):
		# 		print "writing file %r" % (self.torrent.name+".00"+str(i))
		# 		myfile.write(self.torrent.name+".00"+str(i))
		# 	myfile.close()
		for filename in sorted(iglob(os.path.join(PATH, self.torrent.name+".*")), key=self.sort_numbers):
			shutil.copyfileobj(open(filename, 'rb'), self.destination)
		self.destination.close()
		print "---------------------------------------------------------------FINAL FILE SAVED!"

		#self.piece_file = open("")