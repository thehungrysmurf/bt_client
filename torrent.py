import bencode
import hashlib

class Torrent(object):
	def __init__(self, torrent_file):
		with open (torrent_file, 'r') as t:
			parsed_torrent = t.read()
		self.info_dict = bencode.bdecode(parsed_torrent)
		self.tracker_url = self.info_dict['announce']
		self.info_hash = hashlib.sha1(bencode.bencode(self.info_dict['info'])).digest()
		self.info_hash_readable = hashlib.sha1(bencode.bencode(self.info_dict['info'])).hexdigest()
		self.peer_id = '-SG00011234567890123' 
		if self.info_dict.get('name'):
			self.name = self.info_dict['name']
		self.encoding = self.info_dict.get('encoding', None)
		if self.info_dict.get('files'):
			self.no_of_files = len(self.info_dict['files'])
			self.total_length = 0
			for files in self.info_dict['info']['files']:
				self.total_length += files['length']
		else:
			self.no_of_files = 1
			self.total_length = self.info_dict['info']['length']
		#BitTorrent is confusing because it calls these "pieces" but actually they're the blocks that make up the pieces specified in the ['piece length'] field. I'll call them "subpieces".
		self.subpieces = self.info_dict['info']['pieces']
		self.piece_length = self.info_dict['info']['piece length']
		#['pieces'] is a concatenated string of the hashes of each piece (each takes 20 characters). Splitting them up into a list:
		self.list_of_subpieces_hashes = []
		for i in range(0, len(self.subpieces), 20):
			self.list_of_subpieces_hashes.append(self.subpieces[i:i+20])
		self.no_of_subpieces = len(self.list_of_subpieces_hashes)
