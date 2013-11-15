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

    def connect_to_peer(self):
        self.s.settimeout(120)
        self.s.connect((self.peer_ip, self.peer_port))

    def send_message(self, message):
        self.s.send(message)

    # def receive_message(self):
    #     self.s.bind((self.ip, self.port))
    #     running = True
    #     while running:
    #         #ready_to_read, ready_to_write, in_error = select.select([self.s_receive], [self.s_send], [])
    #         for m in ready_to_read:
    #             msg = ''
    #             while len(msg) < MSGLEN:
    #                 chunk = self.s.recv(MSGLEN-len(msg))
    #                 msg = msg + chunk
    #     return msg      

    def receive_message(self, size):
        received = self.s.recv(size)
        return received

    def close_connection_socket(self, ip, port):
        self.s.close()

    
