from torrent import Torrent
from tracker import Tracker
from brain import Brain
import select
import messages
from struct import *
from files import Bitfield

TORRENT_TEST_FILE = '/home/s/Hackbright/my_BT_client/misc/torrents/File_4.torrent'

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
        brain = Brain({ "ip": "localhost", "port": 1050, "id": "-SilviaLearnsBT00000"}, tfile, tracker)
        # When we're ready, we can write this function to have the client listen for other peers to connect to us
        #Brain.listen()

        print "peers: %r" % tracker.peers

        brain.connect_all(3)
        brain.run()


        print "~~~ Done ~~~"

if __name__=="__main__":
        main()
