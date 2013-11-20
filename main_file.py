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

	# Setup Client Peer
	client = Peer({ "ip": "localhost", "port": 1050, "id": "-SG00011234567890123"}, tfile)
	# When we're ready, we can write this function to have the client listen for other peers to connect to us
	client.listen()

	print "peers: %r" % tracker.peers

	# Connect to Peer
	peer = Peer(tracker.peers[2], tfile)
	peer.connect()
	inputs.append(peer)

	running = True
	while running:
		
		ready_to_read, ready_to_write, in_error = select.select(inputs, outputs, [], 3)

		print "select returned"

		for peer in ready_to_read:
			#let the Peer class method handle it - conditions go there
			if not peer.recv_message():
				# Disconnect and remove this peer from the list of inputs we listen to
				print "Peer %s disconnected!" % peer.id
				peer.socket.close()
				inputs.remove(peer)

		# Check for unchoked peers to send request messages
		for peer in inputs:
			if peer.isUnchoked():
				print "Peer %s is unchoked!" % peer.id
				print "Peer %s's Bitfield: %r" % (peer.id, peer.bitfield)
				piece_to_request = client.piece_to_request( peer.bitfield )
				print "piece to request: ", piece_to_request
				if piece_to_request >= 0:
					peer.send_piece_request(piece_to_request)
				else:
					print "Peer %s has nothing I need, disconnecting" % peer.id
					inputs.remove(peer)
					peer.socket.close()

    	# for message_to_peer in ready_to_write:
    	# 	# let the Peer class method handle it, based on conditions determining how to react in the recv_message method
    	# 	# if this doesn't work as is, try putting the messages to be sent in a queue - set condition here: if queue has something, send it.
    	# 	peer.send_next_message(message_to_peer)

	print "done"

if __name__=="__main__":
	main()