#!/usr/bin/env python

"""
align.py

Preprocessed subtitle and audio is used as input to HMM, a model consisting
of a sequence of phonemes, pauses and possible instrumental breaks.
Output a list of aligned word-level time stamp, write this information to file.


Adapted from FAAValign.py (author: Ingrid Rosenfelder) by Chen Liang, 2015
"""


import re, os, codecs, wave, shutil, string


hyphenated = re.compile(r'(\w+)-(\w+)')  # hyphenated words

TEMPDIR = ""
VOWELS = ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH',
          'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']


# apply alignment for a single chuck
def align(wavfile, trs_input, outfile, FADIR='', SOXPATH='', HTKTOOLSPATH=''):
    """call STK forced aligner"""
    # wavfile: sound chuck to be aligned
    # trs_input: list of words from current chuck's lyrics
    # outfile: output result of aligned time in each wave file

    # used for dynamic website applications, should specify paths
    if FADIR:
        os.chdir(FADIR)

    identifier = str(count_chunks)

    # create working directory
    os.mkdir("./tmp" + identifier)

    # prepare wavefile
    SR = prep_wav(wavfile, './tmp' + identifier + '/tmp' + identifier + '.wav', SOXPATH)

    # prepare .mlf(master label file) file
    prep_mlf(trs_input, './tmp' + identifier + '/tmp' + identifier + '.mlf', identifier)

    # prepare scp files
    fw = open('./tmp' + identifier + '/codetr' + identifier + '.scp', 'w')
    fw.write('./tmp' + identifier + '/tmp' + identifier + '.wav ./tmp' + identifier + '/tmp'+ identifier + '.plp\n')
    fw.close()
    fw = open('./tmp' + identifier + '/test' + identifier + '.scp', 'w')
    fw.write('./tmp' + identifier +'/tmp' + identifier + '.plp\n')
    fw.close()

    try:
        if HTKTOOLSPATH:
            system_command_warp(os.path.join(HTKTOOLSPATH, 'HCopy') + ' -T 1 -C ./model/' + str(SR) + '/config -S ./tmp' + identifier + '/codetr' + identifier + '.scp > ./tmp' + identifier + '/someoutput')
            system_command_warp(os.path.join(HTKTOOLSPATH, 'HVite') + ' -T 1 -a -m -I ./tmp' + identifier + '/tmp' + identifier +'.mlf -H ./model/' + str(SR) + '/macros -H ./model/' + str(SR) + '/hmmdefs -S ./tmp' + identifier + '/test' + identifier+ '.scp -i ./tmp' + identifier + '/aligned' + identifier + '.mlf -s 5.0 ' + dicdir + ' ./model/monophones > ./tmp' + identifier + '/someoutput')
        else:
            system_command_warp('HCopy -T 1 -C ./model/' + str(SR) + '/config -S ./tmp' + identifier + '/codetr' + identifier + '.scp > ./tmp' + identifier + '/someoutput')
            system_command_warp('HVite -T 1 -a -m -I ./tmp' + identifier + '/tmp' + identifier +'.mlf -H ./model/' + str(SR) + '/macros -H ./model/' + str(SR) + '/hmmdefs -S ./tmp' + identifier + '/test' + identifier+ '.scp -i ./tmp' + identifier + '/aligned' + identifier + '.mlf -s 5.0 ' + dicdir + ' ./model/monophones > ./tmp' + identifier + '/someoutput')

        # write result of alignment
        write_aligned_output('./tmp' + identifier + '/aligned' + identifier + '.mlf', outfile, SR)

    except Exception, e:
        FA_error = "Error in aligning file %s:  %s." % (os.path.basename(wavfile), e)
        # clean up temporary alignment files
        shutil.rmtree("./tmp" + identifier)
        raise Exception, FA_error

    ## remove tmp directory and all files
    shutil.rmtree("./tmp" + identifier)


def write_aligned_output(infile, outfile, SR):
    """writes the results of the forced alignment ("aligned.mlf") to file as a Praat TextGrid file"""

    f = open(infile, 'rU')
    lines = f.readlines()
    f.close()
    fw = open(outfile, 'w')
    j = 2   # the first line in aligned.mlf including time alignment info
    wrds = []
    vowels = []
    first_v_i = -1
    while (lines[j] != '.\n'):
        ph = lines[j].split()[2]  # phone
        ph = ph[:2]
        if (SR == 11025):  # adjust rounding error for 11,025 Hz sampling rate
            # fix overlapping intervals:  divide time by ten first and round
            st = round((round(float(lines[j].split()[0])/10.0, 0)/1000000.0)*(11000.0/11025.0) + 0.0125, 3)  # start time
            en = round((round(float(lines[j].split()[1])/10.0, 0)/1000000.0)*(11000.0/11025.0) + 0.0125, 3)  # end time
        else:
            st = round(round(float(lines[j].split()[0])/10.0, 0)/1000000.0 + 0.0125, 3)
            en = round(round(float(lines[j].split()[1])/10.0, 0)/1000000.0 + 0.0125, 3)

        if len(lines[j].split()) == 5:  # word level
            wrd = lines[j].split()[4].replace('\n', '')
            if wrd[0] in string.ascii_uppercase:    # it's a word, not a noise or silence or short pause
                vowel = None
                first_v_i = -1
                vowels.append((vowel, None))    # occupy the position for vowel
                wrds.append(wrd)

        if ph in VOWELS and first_v_i == -1:
            vowel = ph
            first_v_i = j
            vowels[-1] = (vowel, st)  # last ele in vowels is 1st vowel in word

        j += 1

    assert(len(vowels) == len(wrds))
    for k in range(len(vowels)):
        fw.write(wrds[k] + '\t')    # word
        fw.write(vowels[k][0] + '\t')   # first vowel
        fw.write(str(vowels[k][1])) # vowel's start time
        fw.write('\n')

    fw.close()


def prep_wav(orig_wav, out_wav, SOXPATH=''):
    """adjusts sampling rate and number of channels of sound file to 16,000 Hz, mono."""
    # NOTE:  wave.py module may require input of 16,000 Hz mono format

    SR = 16000
    if SOXPATH:
        system_command_warp(SOXPATH + ' \"' + orig_wav + '\" -c 1 -r 16000 ' + out_wav)
    else:
        system_command_warp("sox" + ' \"' + orig_wav + '\" -c 1 -r 16000 ' + out_wav)

    return SR


def prep_mlf(transcription, mlffile, identifier):
    """writes transcription to the master label file for forced alignment"""
    # INPUT:
    # list transcription = list of list of (preprocessed) words
    # string mlffile = name of master label file
    # string identifier = unique identifier of process/sound file (can't just call everything "tmp")
    # OUTPUT:
    # none, but writes master label file to disk

    fw = open(mlffile, 'w')
    fw.write('#!MLF!#\n')
    fw.write('"*/tmp' + identifier + '.lab"\n')
    fw.write('sp\n')
    # add noise at beginning
    fw.write("{NS}\n")
    for word in transcription:
        # delete initial asterisks
        if word[0] == "*":
            word = word[1:]
        if word in cmudict:
            fw.write(word + '\n')
            fw.write('sp\n')
        else:
            print "\tWarning!  Word %s not in CMU dict!!!" % word.encode('ascii', 'replace')
    # add noise at the end
    fw.write("{NS}\n")
    fw.write('.\n')
    fw.close()


# main function for align.py
def run(wavfile, subtitle_input, outfile, offset=0.6, FADIR='', SOXPATH='', HTKTOOLSPATH=''):
    """runs the forced aligner for the arguments given"""
    tempdir = os.path.join(FADIR, TEMPDIR)
    global dicdir
    dicdir = os.path.join(FADIR, "model/dict")

    # initialize counter
    global count_chunks
    count_chunks = 0

    # set error message
    global errorMsg
    errorMsg = ""

    # initialize tempdir
    check_tempdir(tempdir)

    # get duration of wavfile
    global duration
    duration = get_duration(wavfile)

    # read CMU dict
    global cmudict
    cmudict = read_dict(os.path.join(FADIR, dicdir))

    # set main output list
    main_out = []

    # read subtitle file
    subListOfLines = read_subtitle(subtitle_input)

    # pre-process subtitle file
    subListOfInfo = parse_subtitle(subListOfLines)

    # start alignment for each chuck(lyrics line)
    for infoLine in subListOfInfo:
        count_chunks += 1
        beg = infoLine[0][0]
        end = infoLine[0][1]
        dur = end - beg
        if offset:  # some subtitles are faster than music
            beg += 0.65
            end += 0.65

        if dur < 0.05:
            print "\tWARNING!  Annotation unit too short (%ss)." % dur
            print "\tSkipping alignment for annotation unit"
            continue

        ## call SoX to cut the corresponding chunk out of the sound file
        chunkSound_name = "_".join([os.path.splitext(os.path.basename(wavfile))[0], "chunk", str(count_chunks)]) + ".wav"
        chuckSound_path = os.path.join(tempdir, chunkSound_name)
        try:
            cut_chunk(wavfile, chuckSound_path, beg, dur, SOXPATH)
        except Exception:
            errorMsg = "Error! Cannot extract sound chunk %s" % chuckSound_path
            print errorMsg
            return errorMsg

        # align chuck
        chuckOut_name = os.path.splitext(chunkSound_name)[0] + ".out"
        chuckOut_path = os.path.join(tempdir, chuckOut_name)
        try:
            align(chuckSound_path, infoLine[1], chuckOut_path, FADIR, SOXPATH, HTKTOOLSPATH)
        except Exception:
            errorMsg = "Error! Alignment failed for chuck %i." % count_chunks
            print errorMsg
            try:
                # remove temp files
                os.remove(chuckSound_path)
                os.remove(chuckOut_path)
            except:
                return errorMsg
            return errorMsg

        # change time offset
        chuckResult = addTimeOffset(chuckOut_path, beg)

        # merge
        main_out = merge(chuckResult, main_out)

        # remove
        os.remove(chuckSound_path)
        os.remove(chuckOut_path)

    # write main_out to file
    write_to_final_result(main_out, outfile)


def write_to_final_result(list, file):
    """write main_out list to file"""

    f = open(file, 'w')
    for line in list:
        f.write(line[0] + '\t')  # word
        f.write(line[1] + '\t')  # first vowel
        f.write(str(line[2]))    # time
        f.write('\n')
    f.close()


def merge(inList, outList):
    """merge chuck output to main output"""

    for line in inList:
        outList.append(line)

    return outList


def addTimeOffset(path, beg):
    """add offset to output file"""

    result = []
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        time = line.split()[-1]
        word = line.split()[0]
        vowel = line.split()[1]

        if time:    # if time != None, vowel exists
            time = float(time)
            newTime = time + beg
        else:
            newTime = None

        result.append([word, vowel, newTime])

    return result


def read_subtitle(subtitle_input):
    """reads the transcription file in either ASCII or UTF-16 encoding
       returns a list of lines in the file"""

    try:  # try UTF-16 encoding first
        t = codecs.open(subtitle_input, 'rU', encoding='utf-16')
        lines = t.readlines()
        print "Encoding is UTF-16!"
    except UnicodeError:
        try:  # then UTF-8
            t = codecs.open(subtitle_input, 'rU', encoding='utf-8')
            lines = t.readlines()
            lines = replace_smart_quotes(lines)
            print "Encoding is UTF-8!"
        except UnicodeError:
            print "error!!!!!!!"
            try:  # then Windows encoding
                t = codecs.open(subtitle_input, 'rU', encoding='windows-1252')
                lines = t.readlines()
                print "Encoding is Windows-1252!"
            except UnicodeError:
                t = open(subtitle_input, 'rU')
                lines = t.readlines()
                print "Encoding is ASCII!"

    # pre-process lines
    newLines = []
    for line in lines:
        newLines.append(preprocess_transcription(line))
    return newLines


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
    line = hyphenated.sub(r'\1 \2', line)   ## do this twice for words like "father-in-law"

    return line


def replace_smart_quotes(lines):
    """replace smart quotes in the input file with ASCII equivalents"""
    cleaned_lines = []
    for line in lines:
        line = line.replace(u'\u2018', "'")
        line = line.replace(u'\u2019', "'")
        line = line.replace(u'\u201a', "'")
        line = line.replace(u'\u201b', "'")
        line = line.replace(u'\u201c', '"')
        line = line.replace(u'\u201d', '"')
        line = line.replace(u'\u201e', '"')
        line = line.replace(u'\u201f', '"')
        cleaned_lines.append(line)
    return cleaned_lines


def parse_subtitle(lines):
    """pre-process subtitle lines, return parsed list."""
    # INPUT: list of subtitle lines
    # OUTPUT: list of parsed subtitle lines in form:
    #         [[(start_time, end_time), [word1, word2, ...]], [...], ...]

    good_lines = []
    best_lines = []
    # delete lines without lyrics
    for i in xrange(len(lines)):
        if re.search('[a-zA-Z]', lines[i]):  # has lyrics
            good_lines.append(lines[i])

    # process line with time stamp from next line
    for i in xrange(len(good_lines)):
        line = good_lines[i]
        if i < len(lines) - 1:
            next_line = lines[i + 1]
        else:
            next_line = None
        parsedLine = check_parse_sub_line(line, next_line)
        if parsedLine:
            best_lines.append(parsedLine)

    return best_lines


def check_parse_sub_line(line, next_line):
    """parse line into format: [(start_time, end_time), [word1, word2, ...]]"""

    if next_line:   # next line is not None, this line is not the last line
        end_time_stamp = next_line.strip().split()[0]
        # convert [00:05.37] to second
        end_time = stamp2sec(end_time_stamp)
    else:
        global duration
        end_time = duration  # end of last line is wavfile length

    beg_time_stamp = line.strip().split()[0]
    start_time = stamp2sec(beg_time_stamp)

    # capitalize words
    words = line.strip().split()[1:]
    newWords = [word.upper() for word in words]
    parsedLine = [(start_time, end_time), newWords]

    return parsedLine

def stamp2sec(stamp):
    """convert a subtitle time stamp to second"""

    min = float(stamp[1:3])
    sec = float(stamp[4:9])

    return min * 60 + sec


def get_duration(soundfile):
    """get the duration of a soundfile"""

    f = wave.open(soundfile, 'r')
    sr = float(f.getframerate())
    nx = f.getnframes()
    f.close()
    duration = round((nx/sr), 3)
    print "input wave duration: %fs" % duration

    return duration


def check_tempdir(tempdir):
    """checks that the temporary directory for all alignment "chunks" is empty"""

    if os.path.isdir(tempdir):
        contents = os.listdir(tempdir)
        if len(contents) != 0:
            print "WARNING!  Directory %s is non-empty!" % tempdir
            print "(Files in directory:  %s )" % contents
            ## delete contents of tempdir
            for item in contents:
                os.remove(os.path.join(tempdir, item))


def cut_chunk(wavfile, outfile, start, dur, SOXPATH=""):
    """uses SoX to cut a portion out of a sound file"""

    if SOXPATH:
        command_cut_sound = " ".join([SOXPATH, '\"' + wavfile + '\"', '\"' + outfile + '\"', "trim", str(start), str(dur)])
    else:
        command_cut_sound = " ".join(["sox", '\"' + wavfile + '\"', '\"' + outfile + '\"', "trim", str(start), str(dur)])
    try:
        system_command_warp(command_cut_sound)
    except:
        return 42


def system_command_warp(command):
    """print command on screen"""
    print command
    os.system(command)


def read_dict(f, mode=''):
    """reads the CMU dictionary, returns it as dictionary object."""

    dictfile = open(f, 'rU')
    lines = dictfile.readlines()
    cmudict = {}
    pat = re.compile('  *')                # two spaces separating CMU dict entries
    for line in lines:
        line = line.rstrip()               # remove trailing whitespaces
        line = re.sub(pat, ' ', line)      # reduce all spaces to one
        word = line.split(' ')[0]          # orthographic transcription
        phones = line.split(' ')[1:]       # phonemic transcription
        if mode == 'vowel_only':           # only transcript vowels
            vowels = []
            for phone in phones:
                for VOWEL in VOWELS:
                    if phone.find(VOWEL) != -1:
                        vowels.append(VOWEL)
                        break
            if len(vowels) == 0:           # omit this word if no vowel found
                continue
            phones = vowels
        if word not in cmudict:
            cmudict[word] = phones       # phonemic transcriptions represented as list of lists of phones
    dictfile.close()

    # check that cmudict has entries
    if len(cmudict) == 0:
        print "WARNING!  Dictionary is empty."

    return cmudict

if __name__ == '__main__':
    wavfile = "./data/default-Blank_Space.wav"
    subtitle_input = "./data/default-Blank_Space.subtitle"
    outfile = "./data/default-Blank_Space.result"
    run(wavfile, subtitle_input, outfile)