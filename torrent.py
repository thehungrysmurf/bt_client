import bencode
import hashlib
from bitfield import Bitfield

class Torrent(object):
	"""Parses a torrent file and extracts useful info"""

	def __init__(self, torrent_file):
		with open (torrent_file, 'r') as t:
			parsed_torrent = t.read()
		self.info_dict = bencode.bdecode(parsed_torrent)
		self.tracker_url = self.info_dict['announce']
		self.info_hash = hashlib.sha1(bencode.bencode(self.info_dict['info'])).digest()
		self.info_hash_readable = hashlib.sha1(bencode.bencode(self.info_dict['info'])).hexdigest()
		
		if self.info_dict['info'].get('name'):
			self.name = self.info_dict['info']['name']
		self.encoding = self.info_dict.get('encoding', None)
		
		if self.info_dict['info'].get('files'):
			self.no_of_files = len(self.info_dict['info']['files'])
			self.total_length = 0
			for files in self.info_dict['info']['files']:
				self.total_length += files['length']
		
		else:
			self.no_of_files = 1
			self.total_length = self.info_dict['info']['length']
		
		self.subpieces = self.info_dict['info']['pieces']
		self.piece_length = self.info_dict['info']['piece length']
		#['pieces'] is a concatenated string of the hashes of each piece (each takes 20 characters). Splitting these up into a list:
		self.list_of_subpieces_hashes = []
		for i in range(0, len(self.subpieces), 20):
			self.list_of_subpieces_hashes.append(self.subpieces[i:i+20])
		self.no_of_subpieces = len(self.list_of_subpieces_hashes)
		self.bitfield = Bitfield(self)
		self.block_size = 16384

	def print_info(self):
		"""Displays some info about the file as specified in the torrent"""

		#print "************Complete metainfo: ", self.info_dict
		# print "************Piece length: ", self.piece_length
		# print "************Tracker URL: ", self.tracker_url
		# print "************No. of subpieces: ", self.no_of_subpieces
		# #print "************List of hashes of subpieces: ", self.list_of_subpieces_hashes
		# print "************Info hash: ", self.info_hash.encode('base64')
		print "We're about to download this file: %r" %self.name
