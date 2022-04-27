#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Load German lyrics from lyricsmania.com
#  Author: Eric Scheibler   (email[at]eric-scheibler[dot]de)
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#


import requests, argparse, sys, re
from subprocess import Popen, PIPE, STDOUT

base_url = "http://www.lyricsmania.com"

def download_page(url):
    r = requests.get(url)
    r.encoding = "utf-8"
    p = Popen(["pandoc", "-f", "html", "-t", "markdown"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    return p.communicate(input=r.text.encode("utf-8"))[0]

parser = argparse.ArgumentParser(description="Lyrics parser for www.darklyrics.com")
parser.add_argument("artist", nargs="?", default="", help="Song artist")
parser.add_argument("title", nargs="?", default="", help="Song title")
args = parser.parse_args()
if args.artist == "":
    print("Song artist missing")
    sys.exit(1)
if args.title == "":
    print("Song title missing")
    sys.exit(1)


#print("%s/searchnew.php?k=%s+%s" % (base_url, \
        args.artist.replace(" ","+"), args.title.replace(" ","+")))


# load results page
result_page = download_page("%s/search.php?k=%s+%s" % (base_url, \
        args.artist.replace(" ","+"), args.title.replace(" ","+")))
song_url = ""
song_id_on_page = ""
song_part_found = False
result_page = str(result_page)
for line in result_page.split(r"\n"):
    #print(line)
    if "![]" in line:
        song_part_found = True
        continue
    if song_part_found and "](" in line:
        #print(line)
        song_url = line.split("](")[1].split(" ")[0]
        break
#print(song_url)
if song_url == "":
    sys.exit(2)

# parse songtext website
result_page = download_page("%s/%s" % (base_url, song_url))
#print(result_page)
lyrics = ""
lyrics_start = False
empty_line_detected = False
for line in result_page.splitlines():
    #print(line)
    #if line.startswith(b"### "):
        #if args.artist.lower() != line[4:].lower():
            #sys.exit(3)
    if b"rel=\"nofollow\"" in line:
        lyrics_start = True
        lyrics = "%s\n" % re.sub(r'\*\*.*\*\*(.*)', r'\1', str(line)).strip()
        continue
    if lyrics_start and ( \
            b"credits" in line): #or \
            #line.startswith(b"[")):
        break
        #print()
    if lyrics_start:
        line = str(line).replace("\\", "").strip()
        if line == "":
            if empty_line_detected == False:
                lyrics += "\n"
                empty_line_detected = True
        else:
            lyrics += "%s\n" % str(line)
            empty_line_detected = False

print(lyrics[:lyrics.__len__()-5])
sys.exit(0)
