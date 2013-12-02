Another BitTorrent Client
=========================

Some context about BT
---------------------
[ ... ]

What it does
------------
My client opens and parses a torrent file to get information about a file that it intends to download. It then connects to the tracker specified in the torrent file to obtain a list of peers who have parts or all of the file. From this list, it chooses 3 (arbitrary number) peers at random to connect to. The client implements the BitTorrent Protocol to communicate with the peers and negotiate the transfer of the file's pieces. When all the pieces have been received, the original file is reassembled on disk. The application is entirely written in Python.

Parsing the torrent
-------------------
A torrent file is a metafile that contains information about the tracker and details that describe the file to be downloaded. This file is encoded ("bencoded") according to the BitTorrent specifications. With the help of the Python bencode library, my client extracts useful information from the torrent:
1. the URL, port and path of the tracker
2. file information:
	- name of the file
	- total file length
	- number of pieces
	- length of each piece
	- hashes of the pieces (used for verification)

Connecting to the tracker
-------------------------
The connection with the tracker is made via an HTTP GET request. The payload of this request contains the tracker's details, my client ID and details about the file extracted from the torrent. The payload of the tracker's response is a list containing the list of peers.
ex. [{ }...{ }]

The BT protocol
---------------
The protocol consists of a series of messages where the peers either describe their state, request pieces or authorize/deauthorize their peers to do something. An overview of the messages and what they mean:

Choked (ID) - "You may not send me requests for pieces" (peer -> client)
Unchoked (ID)- "You may send me requests for pieces" (peer -> client)
Interested (ID) - "I'd like to download this file from you" (client -> peer)
Not Interested (ID) - "I don't want to download anything from you" (client -> peer)
Bitfield (ID)- describes what pieces each peer has (peer <--> client)
Have (ID) - "I have piece of index <x>" (peer -> client)
Request (ID) - "Give me piece of index <x>" (client -> peer)
Piece (ID) - "Here is piece of index <x>" (peer -> client)

Each message begins with a header specifying the length of the message that follows and an ID. Some (like Piece or Bitfield) also have a payload. The messages arrive via TCP in network format, so they have to be unpacked to be readable. In Python, unpacking such a message requires knowing ahead what the message looks like, because the struct library unpacks it according to the format you feed it. 

One of my first notable challenges was formatting valid messages and correctly parsing received messages so I could make meaning from them. Not only is network traffic difficult to grasp because it's encoded and dynamic, but in addition to this each BitTorrent client I talked to has a different personality and might send messages in a different order. The protocol doesn't have clear cut rules for how the messages are to be exchanged - there are only a handful of rules that are imperative (for instance, the handshake must always be first). The rest is entirely unpredictable. 

The Bitfield
------------
The Bitfield message is optional. According to the protocol specifications, if the bitfield is sent at all it must be sent immediately after the handshake. It can be sent either by the client or the peer, and the other end can either send their own bitfield back or not.

In practice though, this message is very useful. Peers have to communicate what pieces they have and don't have in order to locate the pieces they need and request them. The bitfield is an intelligent way of condensing information about posession/absence of many pieces in just a few numbers. When it arrives, a bitfield is a tuple and will look like this: (255, 255, 255, 254). Each number represents the posession/absence of 8 pieces - 1 for each piece the peer has, 0 for pieces they don't have. '255' stands for '11111111', and we arrive at 255 by multiplying each number in the octet by the power of 2 corresponding to that position, from 2^0 to 2^7: 1x2^0 + 1x2^1 + 1x2^3... + 1x2^7 = 255.

An interesting task is, given a bitfield that looks like this (255, 255, 255, 254), to determine whether a given piece of index x (e.g. 20) is a 0 or a 1. I do this by shifting the corresponding octet to the right, and then using that output in a binary AND operation with 1 (00000001). 

The bitfield is also a way for my client to keep track of what pieces it has and which it needs. Whenever it receives a bitfield from a peer, it compares it to its own bitfield and determines which piece to request next. There are many algorithms that you can employ to decide which pieces to request. When I first started sending and receiving messages, I was consistently receiving a Bitfield from the peers immediately after the handshake, regardless of what specific client the peer was using. Although in the official protocol specifications the Bitfield is an optional message, in practice it seems to be the rule. Since it was so obiquitous, and the concept so interesting to work with, I decided to use the Bitfield messages to help me pick a piece to requests. As soon as it receives the Bitfield from a peer, my client compares it to its own bitfield and returns the first piece I need (i.e. is a 0 in my bitfield), if the peer also has it (i.e. is a 1 in peer's bitfield). My client takes all the pieces it can from one client and then moved on to the next peer until the file is complete.

Handling requests
-----------------
Once my client joins the swarm network as a peer, the protocol somewhat takes a life of its own and everything happens very quickly, bound only by the conditions I've specified in the message handler and the conditions that the peer's client has in place. I noticed that the same piece was being requested almost simultaneously from multiple peers (before the bitfield was updated to reflect having the piece), so the piece file was being overwritten every time, but even more alarmingly the bitfield was being updated every time, adding up to an astronomical, incorrect figure. To overcome this, my client keeps a dictionary with all the piece indices as keys. When a piece is requested from a peer, the ID of the peer is assigned as the value to the piece index, "locking" the piece. Peers check the dictionary to make sure the piece is not locked before requesting it.

Putting it all together
-----------------------
I also use the bitfield to ascertain when the file is complete and when it's time to assemble it and clean up the downloads folder. When the client's bitfield is the same as the complete bitfield for that particular file, the client scans the folder for the piece files and concatenates them into the final file, then deletes the pieces.

Real-life considerations
------------------------
Every client is different. 
Some clients don't respect the protocol.

Work in progress
----------------
Adding the server feature.
