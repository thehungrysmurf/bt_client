import bencode

def parse_torrent_file(t):
    parsed = bencode.bdecode(t)
    #parsed = bencode.bdecode(t)
    #trackers = []
    #title
    #number_of_pieces
    #piece_size
    #total_size
    #infohash
    #encoded URL, use requests library to decode it

    return parsed

def main():
    torrent_info_dict = {}
    torrent_file = "/home/user/silvia/[TorrentDownloads.me]_Principles for Open Science   presentation from Kaitlin Thaney 2009 01 05 Creative Commons CC BY.torrent"
    t = open(torrent_file).read()
    parsed = parse_torrent_file(t)
    print "Parsed torrent: "
    for key in parsed.keys():
        if key == 'announce':
            torrent_info_dict['primary tracker'] = parsed[key]

    print "Torrent info: ", torrent_info_dict


main()
