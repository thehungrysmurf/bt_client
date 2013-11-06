import bencode

def parse_torrent(t):
    t_file = open(t).read()
    parsed = bencode.bdecode(t_file)
    #print "Parsed torrent: ", parsed
    torrent_info_dict = {}
    for key in parsed.keys():
        if key == 'announce':
            torrent_info_dict['Tracker_URL'] = parsed[key]
        if key == 'title':
            torrent_info_dict['Title'] = parsed[key]
        if key == 'encoding':
            torrent_info_dict['Encoding'] = parsed[key]
        if key == 'created by':
            torrent_info_dict['Created by'] = parsed[key]
        if key =='info':
            #key is another dictionary, the "info" dictionary
            info_dict = parsed[key]
            for info_key in info_dict.keys():
                if info_key == 'files':
                    torrent_info_dict['How many files'] = len(info_dict['files'])
                if info_key == 'piece length':
                    torrent_info_dict['Piece length'] = info_dict['piece length']
    return torrent_info_dict

def main():
    torrent_file = "/home/user/silvia/sample_torrents/[TorrentDownloads.me]_Principles for Open Science   presentation from Kaitlin Thaney 2009 01 05 Creative Commons CC BY.torrent"
    torrent_info = parse_torrent(torrent_file)

    for field, value in torrent_info.iteritems():
        print field, " : ", value

main()
