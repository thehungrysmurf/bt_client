import bencode
import parse_torrent
from struct import *

def handshake(torrent_file):
    pstrlen = pack('B', 19)
    pstr = 'BitTorrent protocol'
    reserved = pack('!8x')
    partial_handshake = pstrlen + pstr + reserved
    return partial_handshake

'''def main():
    torrent_file = "/home/user/silvia/my_torrents_as_tracker/file_1.torrent"
    h = handshake(torrent_file)
    print h, len(h)

main()'''

