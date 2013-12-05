A BitTorrent Client
=========================

Some context about BitTorrent
---------------------
BitTorrent (BT) is a network protocol that supports peer to peer sharing, used particularly to transfer large files between users. The files are downloaded in pieces that come from different users simultaneously, which makes the download faster than if the file were pulled from only one location.

BitTorrent protocols move 40% to 60% of internet traffic every day. In 2009, the most popular torrent clients had more users than Facebook and YouTube combined. So torrents are a substantial presence on the Internet. Even though much of what's downloaded via BT is not ethical to share, the technology itself should not be considered in a negative light. BitTorrent makes transferring more efficient and increases the availability of materials which are meant to be shared. 

What my program does
------------
My client opens and parses a torrent file to get information about a file that it intends to download. It then connects to the tracker specified in the torrent file to obtain a list of peers who have parts or all of the file. From this list, it chooses 3 peers at random to connect to. The client implements the BitTorrent Protocol to communicate with the peers and negotiate the transfer of the file's pieces. When all the pieces have been received, the original file is reassembled on disk. The application is entirely written in Python.


Parsing the torrent
-------------------
A torrent file is a metafile that contains information about the tracker and details that describe the file to be downloaded. This file is encoded ("bencoded") according to the BitTorrent specifications. From the torrent, my client extracts useful information:
1. The URL, port and path of the tracker
2. File information:
	- Name of the file
	- Total file length
	- Number of pieces
	- Length of each piece
	- Hashes of the pieces (used for verification)

![torrent file](https://raw.github.com/thehungrysmurf/bt_client/master/screenshots/bt_4.png)

Connecting to the tracker
-------------------------
The connection with the tracker is made via an HTTP GET request. The payload of this request contains the tracker's details, my client ID and details about the file extracted from the torrent. The payload of the tracker's response is a list containing the list of peers.

ex. [{u'ip': u'127.0.0.1', u'id': u'-qB2970-457jdJT4KMSJ', u'port': 6881}, {u'ip': u'127.0.0.1', u'id': u'-KT4130-A5PpFR7ws7zp', u'port': 6890}, {u'ip': u'127.0.0.1', u'id': u'-TR2510-mb2qde0zrch1', u'port': 51413}]

The BT protocol
---------------
The protocol consists of a series of messages where the peers either communicate their state, request pieces or authorize/deauthorize their peers to do something. An overview of the messages and what they mean:

- Choked (ID 0) - "You may not send me requests for pieces" (peer -> client)
- Unchoked (ID 1)- "You may send me requests for pieces" (peer -> client)
- Interested (ID 2) - "I'd like to download this file from you" (client -> peer)
- Not Interested (ID 3) - "I don't want to download anything from you" (client -> peer)
- Have (ID 4) - "I have piece of index <x>" (peer -> client)
- Bitfield (ID 5)- describes what pieces each peer has (peer <--> client)
- Request (ID 6) - "Give me piece of index <x>" (client -> peer)
- Piece (ID 7) - "Here's piece of index <x>" (peer -> client)

Each message begins with a header specifying the length of the message that follows, and an ID. Some (like "Piece" and "Bitfield") also have a payload. The messages arrive via TCP in network format, so they have to be unpacked to be readable. In Python, unpacking such a message requires knowing ahead what the message looks like, because the 'struct' library unpacks it according to the format you feed it.

![BT protocol](https://raw.github.com/thehungrysmurf/bt_client/master/screenshots/bt_1.png)

One of the first notable challenges was formatting valid messages and correctly parsing received messages so I could make meaning from them. Not only is network traffic difficult to grasp because it's encoded and dynamic, but in addition to this each BitTorrent client I talked to has a different personality and might send messages in a different order. The protocol doesn't have clear cut rules for how the messages are to be exchanged - there are only a handful of rules that are imperative (for instance, the handshake must always be first). The rest is unpredictable. 

The Bitfield
------------
The Bitfield message is optional. According to the protocol specifications, if the Bitfield is sent at all it must be sent immediately after the handshake. It can be sent either by the client or the peer, and the other end can either send their own Bitfield back or not.

In practice though, this message is very useful. Peers have to communicate what pieces they have and don't have in order to locate the pieces they need and request them. The bitfield is an intelligent way of condensing information about posession/absence of many pieces in just a few numbers. When it arrives, a Bitfield payload is a tuple and will look like this: (255, 255, 255, 254). Each number represents the posession/absence of 8 pieces - 1 for each piece the peer has, 0 for pieces they don't have. 

ex. '255' stands for '11111111', and we arrive at 255 by multiplying each number in the octet by the power of 2 corresponding to that position, from 2^0 to 2^7: 1 x 2^0 + 1 x 2^1 + 1 x 2^3... + 1 x 2^7 = 255.

An interesting task is, given a bitfield that looks like this (255, 255, 255, 254), to determine whether a given piece of index x (ex. 20) is a 0 or a 1. I do this by shifting the corresponding octet to the right, and then using that output in a binary AND operation with 1 (00000001). 

The bitfield is also a way for my client to keep track of what pieces it has and which it needs. When it receives a bitfield from a peer, it compares it to its own bitfield and determines which piece to request next. There are many algorithms that can be used to decide which pieces to request. When I first started sending and receiving messages, I was consistently receiving Bitfields from the peers immediately after the handshake, regardless of what client the peer was using. Even though in the specifications the Bitfield is an optional message, in practice it turns out that most clients send it. 

Since it was so obiquitous, and the concept so interesting to work with, I decided to use the Bitfield messages to help me pick a piece to request. When it receives the Bitfield from a peer, my client compares it to its own bitfield and returns the very first piece I need (i.e. is a 0 in my bitfield) AND that the peer also has (i.e. is a 1 in peer's bitfield). My client takes all the pieces it can from one peer and then moves on to the next peer until the file is complete.

Handling requests
-----------------
Once my client joins the swarm network as a peer, the protocol takes a life of its own and everything happens very quickly, bound by the conditions I've specified in the message handler and the conditions that the peer's client has in place. 

![requesting pieces](https://raw.github.com/thehungrysmurf/bt_client/master/screenshots/bt_2.png)

Running the client with larger files, I noticed that the same piece was being requested from multiple peers and these requests were issued almost simultaneously, before the bitfield had been updated to reflect having the piece. So piece files were being overwritten every time, but even more alarmingly the bitfield was being updated every time, adding up to an astronomical, incorrect figure. To overcome this, my client keeps a dictionary with all the piece indices as keys. When a piece is requested from a peer, the ID of the peer is assigned as the value to the piece index, "locking" the piece. Peers check the dictionary to make sure a piece is not locked before requesting it.

Putting it all together
-----------------------
I also use the bitfield to check when the file is complete and it's time to assemble it. When the client's bitfield is the same as the complete bitfield for that particular file, the client scans the downloads folder for the piece files and concatenates (binary writes) them into the final file, then deletes the pieces.

![saving pieces](https://raw.github.com/thehungrysmurf/bt_client/master/screenshots/bt_3.png)

Real-life considerations
------------------------
Even though I wrote a client that follows the BitTorrent Protocol, when I was testing my client interacting with other clients I learned that not all clients respect the protocol also. For instance, some of the clients occasionally don't honor requests for pieces, which is neither the prescribed behavior on a connection that is Unchoked, nor is it fair play. Another unexpected issue is that Transmission does not seem to respond to handshakes if the connection is closed and reopened from a different socket, and it seems to be the only client that behaves this way.

So perhaps the biggest challenge in this project has been dealing with real-life circumstances. Every client has its idiosyncrasies, and every tracker does too. My local setup involves a QBitTorrent embedded tracker that runs locally, and I used the builtin torrent "wizard" in QBitTorrent to create the torrent metafiles for my files. When I started testing my client with real trackers, the trackers each seemed to encode the peers in a different way, altering the conventions prescribed by the protocol. To create a universal BitTorrent client, one that would work with every tracker and every client, I would need to spend a lot of time testing compatibility with already existing tools that are widely used.

Work in progress
----------------
The socket select statement I'm using to handle the interaction with the peers is limited. Overall, it seems to give preference to one of the peers and process more messages from this peer than from the others. So my file ends up being mostly from one user. For this to be a web of truly simultaneous processes, my application needs to be multi-threaded. I'm now working on implementing threads, so that the transaction with each peer happens independently from the others. The piece dictionary and the bitfield updating are critical sections, so the threads will have to acquire a lock to edit these elements.

My next task is adding the Server part to the client. A good BitTorrent client doesn't just download, but also serves files. I have the messaging protocol already in place, so I only need to add the rules for the message flow when a peer asks for a file. I'm now adding a listening socket and creating a 'Server(Peer)' class that responds to connections accordingly, and in my 'Piece' class I'm building methods that divide the file up into blocks according to the parameters of the request.
