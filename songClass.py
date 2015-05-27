import align, re


# global variable
hyphenated = re.compile(r'(\w+)-(\w+)')  # hyphenated words

class FakeDefaultSong(object):
    def __init__(self, name):
        self.name = name

    def setWav(self, dir):
        self.song = DefaultSong(dir)
        self.song.name = self.name
        if self.name == "Creep" or self.name == "creep":
            self.song.subtitle = "./data/default-Creep.subtitle"
            print "hered"
        elif self.name == "Blank Space" or self.name == "blank space":
            self.song.subtitle = "./data/default-Blank_Space.subtitle"

class FakeMusiXmatchSong(object):
    def __init__(self, name):
        self.name = name

    def setWav(self, dir):
        self.song = MusiXmatchSong(dir)
        self.song.name = self.name

class Song(object):
    def __init__(self, dir):
        self.name = ""
        self.subtitle = None
        self.url = dir
        self.f = open(dir)

    # `__eq__` is used for the peak stream management
    def __eq__(self, other):
        return self.url == other.url

    # this is used by the player as the data interface
    def readPacket(self, bufSize):
        return self.f.read(bufSize)

    def seekRaw(self, offset, whence):
        r = self.f.seek(offset, whence)
        return self.f.tell()

    def align_subtitle(self):
        output = self.url[:-3] + "result"   # store result
        referenceFile = self.url[:-3] + "reference"
        print "lalala:", self.url, self.subtitle
        align.run(self.url, self.subtitle, output)

        # get lyrics
        lyrics = self.getLyrics(self.subtitle)

        # get references and stamps
        with open(referenceFile, "r") as rf:
            references = rf.readlines()
        with open(output, "r") as of:
            stamps = of.readlines()

        refInfoList = []
        resultInfoList = []

        for i in xrange(len(stamps)):
            resultInfo = stamps[i].split()
            resultTime = float(resultInfo[-1])
            resultWord = resultInfo[0]
            resultInfoList.append([resultTime, resultWord])

            if i < len(references):
                refInfo = references[i].split()
                refTime = float(refInfo[-1])
                refWord = refInfo[0]
                refInfoList.append([refTime, refWord])

        # merge words in one lyrics line, reuse var references and stamps
        index = 0
        stamps = [[] for i in range(len(lyrics))]
        references = [[] for i in range(len(lyrics))]
        for i in range(len(lyrics)):
            line = lyrics[i]
            unProcessedLine = line[-1]  # the content of each lyrics line
            line = self.preprocess_transcription(unProcessedLine)  # pre-process
            unProcessedWords = unProcessedLine.split()
            words = line.split()
            for j in range(len(words)):
                # for stamps
                if index < len(resultInfoList):
                    # in a line in stamps, append [time, j]
                    # j is the index of word in a sentence
                    if words[j].upper().find(resultInfoList[index][-1]) != -1:
                        try:    # in processed words but not in lyrics
                            if unProcessedWords[j] != resultInfoList[index][-1]:
                                if unProcessedWords[j].upper().find(resultInfoList[index][-1]) != -1:
                                    stamps[i].append([resultInfoList[index][0], j])
                                elif unProcessedWords[j-1].upper().find(resultInfoList[index][-1]) != -1:
                                    stamps[i].append([resultInfoList[index][0], j-1])

                            else:
                                stamps[i].append([resultInfoList[index][0], j])
                        except:
                            if unProcessedWords[-1].upper().find(resultInfoList[index][-1]) != -1:
                                stamps[i].append([resultInfoList[index][0], len(unProcessedWords)-1])

                # for references
                if index < len(refInfoList):
                    if words[j].upper().find(refInfoList[index][-1]) != -1:
                        try:
                            if unProcessedWords[j] != refInfoList[index][-1]:
                                if unProcessedWords[j].upper().find(refInfoList[index][-1]) != -1:
                                    references[i].append([refInfoList[index][0], j])
                                elif unProcessedWords[j-1].upper().find(refInfoList[index][-1]) != -1:
                                    references[i].append([refInfoList[index][0], j-1])
                            else:
                                references[i].append([refInfoList[index][0], j])
                        except:
                            if unProcessedWords[-1].upper().find(refInfoList[index][-1]) != -1:
                                references[i].append([refInfoList[index][0], -1])
                index += 1

        return lyrics, references, stamps

    @staticmethod
    def preprocess_transcription(line):
        """preprocesses transcription input for CMU dictionary lookup"""

        # some fixing on subtitles
        line = line.replace('high school', 'highschool')
        line = line.replace(' - ', ' -- ')
        # delete punctuation marks
        for p in [',', '.', ':', ';', '!', '?', '"', '%', '--']:
            if line.find("]") != -1:
                bracketRInd = line.find("]")
                last = line[bracketRInd:]
                last = last.replace(p, ' ')  # replace p with space
                last = re.compile(r"\d").sub(" ", last)  # replace digit with space
                line = line[:bracketRInd] + last
        # delete initial apostrophes
        line = re.compile(r"(\s|^)'\b").sub(" ", line)
        # truncation dash will become a word
        line = line.replace(' - ', '')

        # split hyphenated words
        line = hyphenated.sub(r'\1 \2', line)
        line = hyphenated.sub(r'\1 \2', line)   # do this twice for words like "father-in-law"

        return line

    @staticmethod
    def getLyrics(subtitleFile):
        # return list in format [[time, content], [...], ...]

        with open(subtitleFile, "r") as sf:
            lines = sf.readlines()

        lyrics = []
        for line in lines:
            index = line.find("]")
            if index != -1:
                time = line[:index + 1]
                content = line[index + 1:]
                if len(content.split()):    # this line has content
                    content = content.strip()
                    min = float(time[1:3])
                    sec = float(time[4:9])
                    time = min * 60 + sec
                    lyrics.append([time, content])

        return lyrics


class DefaultSong(Song):
    # songs with local subtitles and references
    def __init__(self, dir):
        super(DefaultSong, self).__init__(dir)



class MusiXmatchSong(Song):
    # songs with online subtitles fetched through MusiXmatch, without references
    def __init__(self, dir):
        super(MusiXmatchSong, self).__init__(dir)
        self.subtitleDir = "fetch url"