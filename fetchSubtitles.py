#!/usr/bin/env python
"""
fetchSubtitles.py

Downloading subtitles from the pyMusixMatch wrapper.

(c) 2015, Chen Liang
"""

import os
import sys
import json
from musixmatch import track as TRACK

# construct file path
def getPath(filename = ""):
    homepath = os.getenv('USERPROFILE') or os.getenv('HOME')
    projPath = homepath + os.sep + "Desktop" + os.sep + "MusiXmatch_Data"

    if (not os.path.exists(projPath)):
        os.makedirs(projPath)
        assert(os.path.exists(projPath))
    return projPath + os.sep + filename

# write subtitle dictionary into json format
def writeJsonFile(input, filename, mode="w"):
    with open(filename, mode) as fout:
        json.dump(input, fout)

# write subtitle into subtitle file
def writeSubtitleFile(input, filename, mode="wt"):
    with open(filename, mode) as fout:
        fout.write(input)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in \
            ('help', '-help', '--help', 'h', '-h', '--h'):
        print
        print 'fetchSubtitles.py'
        print 'USAGE'
        print '   python fetchSubtitles.py'
        print '          #download Creep\'s subtitle, used as standard input'
        print '   python fetchSubtitles.py inputSet'
        print '          #download subtitles for standard input set'
        print '   python fetchSubtitles.py genreSet'
        print '          #download subtitles for a specific genre'
        print '          #gerneSet choose from Rock or Pop'
        sys.exit(0)

    # download sample subtitles from song Blank_Space and Creep
    # reason of song choice: To see if American English is needed for matching training model
    if len(sys.argv) < 2:
        trackBS = TRACK.Track(74376920)
        print "*********** TRACK Blank Space ACQUIRED ************"
        trackC = TRACK.Track(20031322)
        print "*********** TRACK Creep ACQUIRED ************"

        # write subtitle to json file
        subtitle_dict_BC = trackBS.subtitles()
        fileName = "default-Blank_Space.json"
        writeJsonFile(subtitle_dict_BC, getPath(fileName))

        subtitle_dict_C = trackC.subtitles()
        fileName = "default-Creep.json"
        writeJsonFile(subtitle_dict_C, getPath(fileName))

        # write subtitle
        subtitleBC = subtitle_dict_BC["subtitle_body"]
        #print subtitle
        fileName = "default-Blank_Space.subtitle"
        writeSubtitleFile(subtitleBC, getPath(fileName))

        # write subtitle
        subtitleC = subtitle_dict_C["subtitle_body"]
        #print subtitle
        fileName = "default-Creep.subtitle"
        writeSubtitleFile(subtitleC, getPath(fileName))

        # exit
        print "*********** DOWNLOAD SUCCEED ************"
        sys.exit(0)

    # download subtitles from mixed genres to create a standard input set
        # NOT IMPLEMENTED
    # download subtitles from a certain genre
    # to show the alignment algorithm's preferences
        # NOT IMPLEMENTED