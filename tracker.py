from torrent import Torrent
import re
import bencode
import requests

class Tracker(object):
	def __init__(self, url):
		m = re.search('https?://(.*):(\d*)(.*)$', url)
		self.host = m.group(1)
		self.port = m.group(2)
		self.path = m.group(3)
		self.peers = []
		print "Setting up tracker with host: %s  port: %s  path: %s" % (self.host, self.port, self.path)
		#self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		pass

	def connect(self, torrent):
		payload = {'info_hash': torrent.info_hash, 'peer_id': torrent.peer_id, 'ip': self.host, 'port': self.port, 'uploaded': 0, 'downloaded': 0, 'left': torrent.total_length, 'event': 'started'}
		peers_from_tracker = requests.get(torrent.tracker_url, params = payload)
		self.peers = bencode.bdecode(peers_from_tracker.text)['peers']


