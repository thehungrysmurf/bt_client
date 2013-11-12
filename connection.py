import bencode
from torrent import Torrent
import requests
import socket
import messages

class InitiateConnection(object):
    def __init__(self, peer_ip, peer_port):
        self.ip = '192.168.1.6'
        self.port = 1050
        #self.peers_from_tracker = send_request_to_tracker(torrent)
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        """#connect to the first peer in the list received from the tracker who is not yourself:
            for peer in peers_dictionary['peers']:
                if peer['id'] != peer_id:
                    tcp_host = peer['ip']
                    print "TCP host: ", tcp_host
                    tcp_port = peer['port']
                    print "TCP port: ", tcp_port
                    break"""

    def connect_to_peer(self):
        self.s.connect((self.peer_ip, self.peer_port))

    def send_message(self, message):
        self.s.send(message)

    def receive_message(self, size):
        received = self.s.recv(size)
        return received

    def close_connection_socket(self, ip, port):
        self.socket.close()

    def send_request_to_tracker(self, torrent):
        payload = {'info_hash': torrent.info_hash, 'peer_id': torrent.peer_id, 'ip': self.ip, 'port': self.port, 'uploaded': 0, 'downloaded': 0, 'left': torrent.total_length, 'event': 'started'}
        #make sure you refer to "connection.peers_from_tracker" only once, so it doesn't send multiple requests to the tracker:
        peers_from_tracker = requests.get(torrent.tracker_url, params = payload)
        return bencode.bdecode(peers_from_tracker.text)

        # this is what the peers_from_tracker dictionary looks like:
        # {'peers': [{'ip': '10.1.10.25', 'id': '-qB2970-QUVDu5V1VmZ1', 'port': 6881}, {'ip': '10.1.10.25', 'id': '-SG00011234567890123', 'port': 1050}, {'ip': '10.1.10.25', 'id': '-TR2510-gu6z89jkpxd2', 'port': 51413}], 'interval': 1800}

    def generate_handshake_to_peer(self, torrent):
        partial_handshake = messages.handshake(torrent)
        complete_handshake = partial_handshake + torrent.info_hash + torrent.peer_id
        return complete_handshake
