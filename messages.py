import bencode
import parse_torrent
from struct import pack

def handshake(torrent_file):
    prefix = '19'
    pstr = "BitTorrent protocol"
    info_hash = parse_torrent.get_infohash(torrent_file)
    peer_id = parse_torrent.peer_id
    return pack(prefix, pstr, '8s', info_hash, peer_id)

def main():
    torrent_file = "/home/user/silvia/my_torrents_as_tracker/File_2_try_2.torrent"
    h = handshake(torrent_file)
    print h

main()

