import hashlib
import glob
import shutil
import os
import re

PATH = 'Downloads'

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
		"""Checks the piece hash against hash from torrent file"""

		if hashlib.sha1(self.data).digest() == self.torrent.list_of_subpieces_hashes[self.index]:
			return True
		else:
			return False

	def write_to_disk(self):
		"""Saves the data to disk"""

		print "--------------------------------------------------------WRITING PIECE %r TO DISK" %self.index
		try:
			os.makedirs(PATH)
		except:
			pass
		self.piece_file_name = os.path.join(PATH, self.torrent.name+'.'+'00'+str(self.index))
		print "Saving piece to file name: ", self.piece_file_name
		piece_file = open(self.piece_file_name, 'w')
		piece_file.write(self.data)
		piece_file.close()	
	
	def sort_numbers(self, value):
		"""Creates key for sorting the piece files so that they're actually in numerical order (i.e. 10 comes after 9, not before)""" 

		numbers = re.compile(r'(\d+)')
		parts = numbers.split(value)
		parts[1::2] = map(int, parts[1::2])
		return parts

	def concatenate_pieces(self):
		"Assembles pieces into file"

		print "Concatenating pieces into final file..."
		self.final_file_name = os.path.join(PATH, self.torrent.name)
		self.destination = open(self.final_file_name, 'wb')
		for filename in sorted(glob.glob(os.path.join(PATH, self.torrent.name+".*")), key=self.sort_numbers):
			shutil.copyfileobj(open(filename, 'rb'), self.destination)
		self.destination.close()
		print "---------------------------------------------------------------FINAL FILE SAVED!"
		self.delete_piece_files()

	def delete_piece_files(self):
		"""Moves piece files to 'Pieces' folder"""

		print "Removing piece files and cleaning up..."
		pieces_dir = os.path.join(PATH, 'Pieces')
		try:
			os.makedirs(pieces_dir)
		except:
			pass
		for i in range(self.torrent.no_of_subpieces):
			piece_src = os.path.join(PATH, self.torrent.name+'.'+'00'+str(i))
			piece_dest = os.path.join(pieces_dir, self.torrent.name+'.'+'00'+str(i))
			shutil.move(piece_src, piece_dest)
			# Or I just delete them:
			# os.remove(piece_src)