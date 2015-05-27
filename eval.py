import re


# global variable
hyphenated = re.compile(r'(\w+)-(\w+)')  # hyphenated words


def eval_song(name):
    """evaluate aligner's result for a single song."""
    # INPUT: file identifier of the song
    # OUTPUT: there is no output, but result will be written to name.eval

    # NOTE: name.reference, name.result, name.subtitle will be used

    # get reference data
    with open(name + ".reference", "r") as rf:
        references = rf.readlines()
    ref_count = 0
    ref_time = []
    words = []
    for reference in references:
        entries = reference.split()
        if len(entries) > 0:    # not a blank line
            ref_count += 1
            words.append(entries[0])
            ref_time.append(float(entries[-1]))

    # get result data
    with open(name + ".result", "r") as rf:
        results = rf.readlines()
    result_time = []
    for i in xrange(ref_count):
        entries = results[i].split()
        result_time.append(float(entries[-1]))

    # compute
    err = compareOverall(ref_time, result_time)
    errList = compareEachLine(name, ref_time, result_time, words)

    # write evaluation result to file
    with open(name + ".eval", "w") as ef:
        ef.write("overall:\t%fs\n" % err)
        for i in range(len(errList)):
            ef.write("%d\t%f\n" % (errList[i][0], errList[i][1]))


def compareOverall(ref_time, result_time):
    """compute the overall time difference"""

    sum = 0
    for i in range(len(ref_time)):
        sum += abs(ref_time[i] - result_time[i])

    return sum/len(ref_time)


def compareEachLine(name, ref_time, result_time, words_in_ref):
    """compute the time difference for each line of lyrics"""

    with open(name + ".subtitle", "r") as sf:
        lines = sf.readlines()

    index = 0
    resultList = []
    for i in range(len(lines)):
        line = preprocess_transcription(lines[i])
        words = line[line.find("]") + 1:].split()
        if len(words) == 0:
            continue
        sum = 0
        count = 0
        for j in range(len(words)):
            if index == len(words_in_ref):
                return resultList
            if words[j].upper().find(words_in_ref[index]) != -1:
                sum += abs(ref_time[index] - result_time[index])
                index += 1
                count += 1
        resultList.append((i + 1, sum/count))

    return resultList


# copied from align.py
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


eval_song("data/vocal-Creep")