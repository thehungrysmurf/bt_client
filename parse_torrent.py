import bencode
import hashlib
import socket
import requests

peer_id = '-SG00011234567890123'

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
    return infohash

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
    #payload['ip'] = socket.gethostbyname(socket.gethostname())
    request = requests.get(decoded_torrent['announce'], params = payload)
    return bencode.bdecode(request.text)

#This following function is not really necessary, it's just for me to clarify what kind of data I'm getting from the tracker. The function above returns a dictionary containing a list of peers that's easy to work with - "peers" is a list which contains dictionaries with peer info (ip, id and port), one for each peer.

def get_peer_info(torrent_file):
    peer_dict = send_request_to_tracker(torrent_file)
    peer_info = []
    list_of_peers = peer_dict['peers']
    for peer in list_of_peers:
        peer_info.append((peer['ip'], peer['id'], peer['port']))
    return peer_info

def send_request_to_peer(torrent_file):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = send_request_to_tracker(torrent_file)['peers'][0]['ip']
    port = send_request_to_tracker(torrent_file)['peers'][0]['port']
    s.connect((host, port))
    #handshake goes here
    s.send(handshake)

def main():
    torrent_file = "/home/user/silvia/my_torrents_as_tracker/File_2_try_2.torrent"
    torrent_info_dict = get_torrent_info(torrent_file)

    for field, value in torrent_info_dict.iteritems():
        print field, " : ", value

    print "Infohash: ", get_infohash(torrent_file).hexdigest()
    print "Reply from tracker: ", send_request_to_tracker(torrent_file)
    print "Peer info: ", get_peer_info(torrent_file)

main()
