import bencode
import hashlib
import socket
import requests
import messages
from struct import pack, unpack

peer_id = '-SG00011234567890123'
torrent_file = "/home/user/silvia/my_torrents_as_tracker/file_1.torrent"

def get_torrent_info(torrent_file):
    t_file = open(torrent_file).read()
    parsed = bencode.bdecode(t_file)
    #print "Parsed torrent: ", parsed
    torrent_info_dict = {}
    for key in parsed.keys():
        if key == 'announce':
            torrent_info_dict['Tracker_URL'] = parsed[key]
        if key == 'title':
            torrent_info_dict['Title'] = parsed[key]
        if key == 'encoding':
            torrent_info_dict['Encoding'] = parsed[key]
        if key == 'created by':
            torrent_info_dict['Created by'] = parsed[key]
        if key =='info':
            #key is another dictionary, the "info" dictionary
            info_dict = parsed[key]
            for info_key in info_dict.keys():
                if info_key == 'files':
                    torrent_info_dict['How many files'] = len(info_dict['files'])
                if info_key == 'piece length':
                    torrent_info_dict['Piece length'] = info_dict['piece length']
    return torrent_info_dict

def get_infohash(torrent_file):
    decoded_torrent = bencode.bdecode(open(torrent_file).read())
    infohash = hashlib.sha1(bencode.bencode(decoded_torrent['info']))
    return infohash.digest()

def send_request_to_tracker(torrent_file):
    decoded_torrent = bencode.bdecode(open(torrent_file).read())
    payload = {}
    total_length = 0
    payload['info_hash'] = get_infohash(torrent_file)
    payload['peer_id'] = '-SG00011234567890123'
    payload['port'] = 1050
    payload['uploaded'] = 0
    payload['downloaded'] = 0
    files_list = decoded_torrent['info'].get('files', None)
    if files_list:
        for item in decoded_torrent['info']['files']:
            total_length += item['length']
    else:
        total_length += decoded_torrent['info']['length']
    payload['left'] = total_length
    payload['event'] = 'started'
    payload['ip'] = '10.1.10.25'
    peers_dictionary = requests.get(decoded_torrent['announce'], params = payload)
    return bencode.bdecode(peers_dictionary.text)

#This following function is not really necessary, it's just for me to clarify what kind of data I'm getting from the tracker. The function above returns a dictionary containing a list of peers that's easy to work with - "peers" is a list which contains dictionaries with peer info (ip, id and port), one for each peer.

def get_peer_info(torrent_file):
    peer_dict = send_request_to_tracker(torrent_file)
    peer_info = []
    list_of_peers = peer_dict['peers']
    for peer in list_of_peers:
        peer_info.append((peer['ip'], peer['id'], peer['port']))
    return peer_info

def generate_handshake_to_peer(peers_dictionary):
    # this is what peer_dictionary looks like:
    # {'peers': [{'ip': '10.1.10.25', 'id': '-qB2970-QUVDu5V1VmZ1', 'port': 6881}, {'ip': '10.1.10.25', 'id': '-SG00011234567890123', 'port': 1050}, {'ip': '10.1.10.25', 'id': '-TR2510-gu6z89jkpxd2', 'port': 51413}], 'interval': 1800}

    """for peer in peers_dictionary['peers']:
        if peer['id'] != peer_id:
            tcp_host = peer['ip']
            print "TCP host: ", tcp_host
            tcp_port = peer['port']
            print "TCP port: ", tcp_port
            break
    """
    partial_handshake = messages.handshake(torrent_file)
    complete_handshake = partial_handshake + get_infohash(torrent_file) + peer_id
    print "************Sending handshake: ", complete_handshake
    return complete_handshake



def main():
    metainfo = get_torrent_info(torrent_file)
    print "************Metainfo :", metainfo
    peers_dictionary = send_request_to_tracker(torrent_file)
    print "************Response from tracker to HTTP GET request: ", peers_dictionary
    infohash = get_infohash(torrent_file)
    print "Infohash: ", infohash
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_host = '10.1.10.25'
    tcp_port = 51413
    s.connect((tcp_host, tcp_port))
    handshake = generate_handshake_to_peer(peers_dictionary)
    s.send(handshake)
    data = s.recv(len(handshake))
    print "Peer id from peer: ", data[-20:]
    print "Infohash from peer: ", hashlib.sha1(data[-40:-20]).hexdigest()
    print "************Full response handshake from peer: ", data
    """prefix = pack('!LB', 0001)
    message_id = pack('B', 2)
    interested_message = prefix + message_id
    """
    interested_message = "len=0001id=2"
    s.send(interested_message)
    reply = s.recv(len(interested_message))
    print "Len: ", len(reply)
    unpacked_reply = unpack('!12s', reply)
    print "Reply to interested: ", reply
    print "Unpacked: ", unpacked_reply

if __name__ == "__main__":
    main()
