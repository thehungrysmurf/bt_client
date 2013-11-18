from torrent import Torrent
from tracker import Tracker
from peer import Peer
import select
import messages
from struct import *
from files import Bitfield

TORRENT_TEST_FILE = '/home/silvia/Hackbright/my_BT_client/misc/torrents/File_1.torrent'

def main():
	inputs = []
	outputs = []
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
		
		ready_to_read, ready_to_write, in_error = select.select(inputs, outputs, [])

		for peer in ready_to_read:
			#let the Peer class method handle it - conditions go there
			if not peer.recv_message():
				# Disconnect and remove this peer from the list of inputs we listen to
				print "Peer %s disconnected!" % peer.id
				peer.socket.close()
				inputs.remove(peer)

    	# for message_to_peer in ready_to_write:
    	# 	# let the Peer class method handle it, based on conditions determining how to react in the recv_message method
    	# 	# if this doesn't work as is, try putting the messages to be sent in a queue - set condition here: if queue has something, send it.
    	# 	peer.send_next_message(message_to_peer)

	print "done"


if __name__=="__main__":
	main()