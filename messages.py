import bencode
import parse_torrent
from struct import *

def handshake(torrent):
    pstrlen = pack('B', 19)
    pstr = 'BitTorrent protocol'
    reserved = pack('!8x')
    partial_handshake = pstrlen + pstr + reserved
    return partial_handshake

def bitfield():
    #may be sent by the downloader only immediately after handshake is completed & before sending anything else
    #variable length
    #doesn't have to be sent if the downloader has no pieces
    pass

def have():
    #fixed-length, with payload = zero-based index of a piece that was successfully downloaded and verified with hash
    pass

def choke():
    #the initial state of any connection
    #means the peer is not sending you the file until they "unchoke" you: basically "I'm not giving it to you."
    #facilitates a tit-for-tat algorithm for peers to get files
    #fixed-length, no payload
    pass

def unchoke():
    #official BT client has an algorithm for doing this. At any one time only one peer gets unchoked. Which peer gets unchoked rotates every 30 sec
    #fixed-length, no payload
    pass

def keepalive():
    #messages of length 0, sent once every 2 min to prevent timeout
    pass

def interested():
    #fixed-length, no payload
    #client sends to mean = "I would like to download this file from you"
    pass

def uninterested():
    #fixed-length, no payload
    pass

'''def main():
    torrent_file = "/home/user/silvia/my_torrents_as_tracker/file_1.torrent"
    h = handshake(torrent_file)
    print h, len(h)

main()'''

