## Addressing the Problem
### What is the Problem?
We want to make a system that align singing in polyphonic music audio with subtitles, which is basically textual lyrics with time stamp for each line. 

### Difficulties
1. Accompaniment could reduce recognition accuracy.
2. Variability of phonation in singing will also affect the system.

## System Overview
### Solution for Mentioned Difficulties
1. Apply source separation to extract vocal line.
2. Adapt HMM models using singing voice training data to overcome the difference between speech and singing.

### Desired Structure
![Structure](https://farm8.staticflickr.com/7722/18120282265_8ceb5f848d_z.jpg)

### Implementeion
1. Trained HMM using **[ARCTIC]( http://festvox.org/cmu_arctic/)** speech database, while an annoted singing phonemes database is not available.
2. Created phonetic transcription of the subtitle.
3. Use HCopy in HTK to get LPC features of the phonetic transcription.
4. Use HVite in HTK to get Veterbi forced alignment result.

### Things could be Improved
1. Should use singing dataset to adapt this HMM model.
2. Should automatically add entries which are not available for CMU phonemes dictionary.
3. Should apply vocal activity detection.

## Result
### The Alignment output
The alignment error is showed in this table:

| Song | Average | Standard Deviation |
|--------|--------|-|
|   Creep     |   1006ms     | 1.65 |
|   Creep(vocal only)     |    1129ms    | 1.16 |
|   Blank Space     |    429ms    | 0.81 |

After eliminating outliners(error greater than 3s):
~Note:~ ~most~ ~outliners~ ~would~ ~be~ ~improved~ ~by~ ~better~ ~vocal~ ~appearence~ ~detection,~ ~and~ ~some~ ~outliners~ ~are~ ~caused~ ~by~ ~wrongly~ ~labelled~ ~subtitle~ ~files.~

| Song | Average | Standard Deviation |
|--------|--------|-|
|   Creep     |   546ms     | 0.76 |
|   Creep(vocal only)     |    913ms    | 0.83 |
|   Blank Space     |    323ms    | 0.26 |

_ _ _

Graph for each lyrics line's error is as followed:
![Creep](https://farm8.staticflickr.com/7782/17546272983_426fd1c3b4_z.jpg)
![CreepVocal](https://farm8.staticflickr.com/7757/17978973498_9ae5f20db5_z.jpg)
![BlankSpace](https://farm9.staticflickr.com/8762/17979147160_07450cee83_z.jpg)


### Thoughts about the Result

Given the performance between two songs, one guess is the length of lyrics lines provided in subtitle files would influence the detection of words, for that a large portion of accompaniment has been eliminated. Also, if normalized error is measured, the difference between songs might be more alike.

About the effect of vocal separation -- I didn't expect the result would be like this... One thought is our models include noise model, whereas the vocal-only file doesn't include much noise. 

Larger dataset and tests with more songs need to be done.

### A visualization of the output
![app](https://farm8.staticflickr.com/7761/17981486829_f1e2189de3_c.jpg)


## Reference
Mesaros A, Virtanen T. Automatic alignment of music audio and lyrics[C]//Proceedings of the 11th Int. Conference on Digital Audio Effects (DAFx-08). 2008.

Mesaros A. Singing voice identification and lyrics transcription for music information retrieval invited paper[C]//Speech Technology and Human-Computer Dialogue (SpeD), 2013 7th Conference on. IEEE, 2013: 1-10.

Mauch M, Fujihara H, Goto M. Song Prompter: An accompaniment system based on the automatic alignment of lyrics and chords to audio[C]//Late-breaking session at the 10th International Conference on Music Information Retrieval. 2010.