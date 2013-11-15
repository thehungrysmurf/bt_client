from torrent import Torrent
from tracker import Tracker
from peer import Peer
import select
import messages
from struct import *

TORRENT_TEST_FILE = '/home/silvia/Hackbright/my_BT_client/misc/torrents/File_1.torrent'

def main():
	inputs = []
	print "starting"

	# Read & Parse Torrent File
	tfile = Torrent(TORRENT_TEST_FILE)
	tfile.printInfo()

	# Setup our Tracker connection
	tracker = Tracker(tfile.tracker_url)
	tracker.connect(tfile)

	print "peers: %r" % tracker.peers

	# Connect to Peer
	peer = Peer(tracker.peers[2], tfile)
	peer.connect()
	inputs.append(peer)

	running = True
	while running:
		
		ready_to_read, ready_to_write, in_error = select.select(inputs, [], [])

		for peer in ready_to_read:
			peer.recv_message()
			# b = messages.assemble_message("bitfield")
   #  		print "sending bitfield: ", unpack("!IB15s", b)
    		#peer.socket.send(b)
    		i = messages.assemble_message("interested")
    		print "sending interested: ", unpack("!IB", i)
    		peer.socket.send(i)

	print "done"


if __name__=="__main__":
	main()