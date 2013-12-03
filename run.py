#!/usr/bin/env python

from torrent import Torrent
from tracker import Tracker
from brain import Brain
import select
import messages
from struct import *
from bitfield import Bitfield
import random
import sys

# TORRENT_TEST_FILE = '/home/s/Downloads/Musicshake - Irish Fiddle _Celtic_.torrent'

def main(argv):
        if len(argv) != 2:
                print "Usage: %s <torrent-file>" % argv[0]
                sys.exit(1)

        inputs = []
        outputs = []
        print "~~~ Starting BitTorrent Client ~~~"
        print "----------------------------------"

        # Read & parse torrent file
        tfile = Torrent(argv[1])
        tfile.print_info()

        #My ID has to be exactly 20 characters but each ID should be random
        my_id = "-SilviaLearnsBT%05d"%random.randint(0,99999)

        # Setup tracker connection
        tracker = Tracker(tfile.tracker_url)
        tracker.connect(tfile, my_id)

        # Setup Brain, the dispatcher
        brain = Brain({ "ip": "localhost", "port": 1050, "id": my_id}, tfile, tracker)

        if brain.is_complete():
                print "Aborting. I have the entire file!"

        else:
                print "Received list of peers from tracker: %r" % tracker.peers

                brain.add_peers()
                brain.connect_all(3)
                brain.run()

                print "~~~ GROOVY! You successfully downloaded a torrent ~~~"

if __name__=="__main__":
        main(sys.argv)
