from files import Bitfield
from torrent import Torrent
from struct import *

def main():
	tfile = '/home/silvia/Hackbright/my_BT_client/misc/torrents/File_1.torrent'
	t = Torrent(tfile)
	b = Bitfield(t)
	print "0. My bitfield: %r" % b.my_bitfield
	peer_bitfield = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2]
	print "Peer bitfield: %r" %peer_bitfield
	print b.first_piece_that_peer_has(peer_bitfield)
	u = b.update_my_bitfield(10)
	print "1. My bitfield after getting piece of index 10: %r" %b.my_bitfield
	u2 = b.update_my_bitfield(20)
	print "2. My bitfield after getting piece of index 20: %r" %b.my_bitfield
	u3 = b.update_my_bitfield(0)
	print "3. My bitfield after getting piece of index 0: %r" %b.my_bitfield
	u4 = b.update_my_bitfield(118)
	print "4. My bitfield after getting piece of index 118: %r" %b.my_bitfield
	print b.first_piece_i_need()

main()