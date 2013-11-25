from torrent import Torrent
from tracker import Tracker
from peer import Peer
import select
import messages
from struct import *
from files import Bitfield

TORRENT_TEST_FILE = '/home/silvia/Hackbright/my_BT_client/misc/torrents/File_3.torrent'

def main():
	inputs = []
	outputs = []
	print "~~~ Starting BitTorrent Client ~~~"

	# Read & Parse Torrent File
	tfile = Torrent(TORRENT_TEST_FILE)
	tfile.printInfo()

	# Setup our Tracker connection
	tracker = Tracker(tfile.tracker_url)
	tracker.connect(tfile)

	# Setup Client Peer
	client = Peer({ "ip": "localhost", "port": 1050, "id": "-SilviaLearnsBT"}, tfile)
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

		print "...select returned..."

		for peer in ready_to_read:
			#let the Peer class method handle it - conditions go there
			if not peer.recv_message():
				# Disconnect and remove this peer from the list of inputs we listen to
				print "Peer %s disconnected!" % peer.id
				peer.socket.close()
				inputs.remove(peer)

		# Check for unchoked peers to send request messages
		for peer in inputs:
			if peer.is_unchoked():
				print "Peer %s is unchoked!" % peer.id
				print "Peer %s's Bitfield: %r" % (peer.id, peer.bitfield.bitfield)
				print "Client's bitfield: %r" %client.bitfield.bitfield
				piece_to_request = client.piece_to_request( peer.bitfield )
				
				if piece_to_request >= 0:
					while peer.has_piece() < 0 and not peer.requesting:
						print "--------------BEGINNING OF WHILE LOOP---------------"
						print "Client has a piece: %r" %client.has_piece()
						print "Client is requesting: ", client.requesting
						print "Peer has a piece: ", peer.has_piece()
						print "Peer is requesting: ", peer.requesting
						print "Next piece to request: ", piece_to_request
						peer.send_piece_request(piece_to_request, peer.torrent.block_size)
						print "-----------------END OF WHILE LOOP------------------"

				else:
					if client.has_entire_file:
						print "File is complete! No pieces left to download."
						running = False
					else:
						print "Peer %s has nothing I need, disconnecting" % peer.id

					inputs.remove(peer)
					peer.socket.close()
			
			if peer.have >= 0:
				print "---------------------------------------------------------------UPDATING BITFIELD"
				print "I have piece of index %r, let's update my bitfield..." %peer.have
				print "Bitfield before update: %r" %client.bitfield.bitfield
				client.bitfield.update_bitfield(peer.have)
				print "Bitfield after update: %r" %client.bitfield.bitfield
				peer.have = -1
				print "------------------------------------------------------FINISHED UPDATING BITFIELD"

			if peer.complete:
				print "GROOVY! You successfully downloaded a torrent."
				inputs.remove(peer)
				running = False
						
	print "~~~ Done ~~~"

if __name__=="__main__":
	main()