from torrent import Torrent
import re
import bencode
import requests
import struct

class Tracker(object):
	def __init__(self, url):
		print "URL: ", url
		# m = re.search('https?://(.*)(:\d*)(.*)$', url)
		# print "M: ", m
		# self.host = m.group(1)
		# self.port = m.group(2).strip(':')
		# self.path = m.group(3)
		url2 = url.split("://")
		if "/" in url2[1]:
			host_and_port, self.path = url2[1].split("/")
		else:
			host_and_port = url2[1]
		if ":" in url2[1]:
			self.host, self.port = host_and_port.split(':')
		else:
			self.host = host_and_port
			self.port = None 

		self.peers = []
		print "Setting up tracker with host: %s  port: %s  path: %s" % (self.host, self.port, self.path)
		#self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		pass

	def connect(self, torrent):
		payload = {'info_hash': torrent.info_hash, 'peer_id': torrent.peer_id, 'ip': self.host, 'port': self.port, 'uploaded': 0, 'downloaded': 0, 'left': torrent.total_length, 'event': 'started'}
		peers_from_tracker = requests.get(torrent.tracker_url, params = payload)
		# print "HTTPS Response from tracker: %r" %peers_from_tracker.text
		self.peers = bencode.bdecode(peers_from_tracker.text)['peers']
		print "Peers dict: %r" %self.peers, len(self.peers)
		for item in self.peers:
			print item.keys()
			# print "Keys: " %self.peers.keys()
		# print "Peers unpacked: %r" %struct.unpack("!s", self.peers)


