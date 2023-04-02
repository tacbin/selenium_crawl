# -*- coding: utf-8 -*-
import os

if __name__ == '__main__':
    import codecs
    import eyed3

    subtitle_filename = './1.vtt'
    mp3_filename = './1.mp3'
    # import urllib2  # For downloading webpage
    import time  # For pausing
    import eyed3  # For MP3s
    import re  # For replacing characters
    import os  # For reading folders

    # Must make the program stop for a while to minimize server load
    # time.sleep(3)
    # Opening MP3
    mp3 = eyed3.load(mp3_filename)
    # Setting Values
    # artist = mp3.tag.artist.lower()
    # raw_song = str(mp3.tag.title).lower()
    # song = re.sub('[^0-9a-zA-Z]+', '', raw_song)  # Stripping songs of anything other than alpha-numeric characters
    # Generating A-Z Lyrics URL
    # url = "http://www.azlyrics.com/lyrics/" + artist + "/" + song + ".html"
    # Getting Source and extracting lyrics
    # text = urllib2.urlopen(url).read()
    # where_start = text.find('<!-- start of lyrics -->')
    # start = where_start + 26
    # where_end = text.find('<!-- end of lyrics -->')
    # end = where_end - 2

    # Setting Lyrics to the ID3 "lyrics" tag
    with open(subtitle_filename, 'r', encoding='utf-8') as f:
        data = f.read()
        mp3.tag.lyrics.set(data)
        mp3.tag.save()
