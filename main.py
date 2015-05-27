# -*- coding: utf-8 -*-
from Tkinter import *
from eventBasedAnimationClass import EventBasedAnimationClass
import time, random
from songClass import *
import tkFileDialog, tkMessageBox
from customText import CustomText
from musicplayer import createPlayer


class Visualization(EventBasedAnimationClass):
    def __init__(self, width=1000, height=390):
        super(Visualization, self).__init__(width, height)
        self.image_path = "./gif/"
        # self.textWidget = CustomText()
        # self.textWidgetRef = CustomText()

    def initAnimation(self):
        self.inSubScreen = True     # in subtitle upload screen
        self.inAudScreen = False    # in audio upload screen
        self.inAnimationScreen = False
        self.isPaused = False

        self.image_backgound = PhotoImage(file=self.image_path + "background.gif")
        self.canvas.create_image(self.width/2, self.height/2, image=self.image_backgound)
        self.image_pointer = PhotoImage(file=self.image_path + "Fingerright.gif")
        self.image_next = PhotoImage(file=self.image_path + "Rightcirclearrow.gif")
        self.image_load = PhotoImage(file=self.image_path + "iPod.gif")
        self.textWidget = CustomText()
        self.textWidgetRef = CustomText()

        self.isProcessing = False
        self.onPlay = None
        self.nextArrowPos = (1, 1)
        self.startTime = time.time()
        self.initSongs(2)
        self.lyrics = []   # for the on play song
        self.references = []
        self.stamps = []
        self.animationStartTime = 0

        self.loadPos = (self.width/2, 160)

        # init widget
        self.textWidget.config(state=NORMAL)
        self.textWidget.delete(1.0, END)
        self.textWidget.config(state=DISABLED)
        self.textWidgetRef.config(state=NORMAL)
        self.textWidgetRef.delete(1.0, END)
        self.textWidgetRef.config(state=DISABLED)

        # animation screen drawing init
        self.red = random.randint(0, 255)
        self.green = random.randint(0, 255)
        self.currentContent = ""
        self.currentWord = "blablurbobobo"
        self.currentWordRef = "zzzzz"
        self.lineNumber = -1


    def initSongs(self, number):
        # should add randomly got songs from MusiXmatch, fetch subtitle here
        self.posSongBalls = []
        self.setSongBalls(number)
        self.songBalls = [FakeDefaultSong("Creep"),
                          FakeDefaultSong("Blank Space")]


    def onMousePressed(self, event):
        if self.inSubScreen:
            cx, cy = event.x, event.y
            for i in xrange(len(self.songBalls)):  # chose a song ball
                if self.isInside((cx, cy), self.posSongBalls[i]):
                    self.onPlay = self.songBalls[i]

            if self.isInsideCircle((cx, cy), self.nextArrowPos, 28):  # chose next arrow
                self.enterAudScreen()

        if self.inAudScreen:
            cx, cy = event.x, event.y
            loadSqure = (self.loadPos[0] - 14, self.loadPos[1] - 28,
                         self.loadPos[0] + 14, self.loadPos[1] + 28)
            if self.isInside((cx, cy), loadSqure):
                filePath = tkFileDialog.askopenfilename()
                if filePath == "":
                    print "lalalala"
                elif not ".wav" in filePath:  # This is modified from lecture notes
                    message = "Only accept '.wav' files."
                    title = "Warning"
                    tkMessageBox.showinfo(title, message)
                else:
                    self.onPlay.setWav(filePath)
                    self.isProcessing = True
                    self.drawProcessing()
                    # (self.lyrics, self.references, self.stamps) = ([[1, "a"]], [[[1, 0]]], [[[1, 0]]])
                    (self.lyrics, self.references, self.stamps) = self.onPlay.song.align_subtitle()
                    self.enterAnimationScreen()
                    # set Animation start time
                    self.animationStartTime = time.time()
                    print "start time: %f" % self.animationStartTime

                    # play song
                    self.songList = [self.onPlay.song.url]
                    self.player = createPlayer()
                    self.player.outSamplerate = 96000
                    self.player.queue = self.songs()
                    self.player.peekQueue = self.peekSongs
                    self.player.playing = True

    def songs(self):
        while True:
            yield self.onPlay.song

    def peekSongs(self, n):
        return map(Song, self.songList)


    def enterAudScreen(self):
        self.inSubScreen = False
        self.inAudScreen = True

    def enterAnimationScreen(self):
        self.inSubScreen = False
        self.inAudScreen = False
        self.inAnimationScreen = True
        self.isProcessing = False

    @staticmethod
    def isInsideCircle(point, center, radius):
        dif = [abs(point[i] - center[i]) for i in range(2)]
        if dif[0] * dif[0] + dif[1] * dif[1] < radius * radius:
            return True

    @staticmethod
    def isInside(point, square):
        if square[0] < point[0] < square[2] and square[1] < point[1] < square[3]:
            return True

    def redrawAll(self):
        self.canvas.delete(ALL)
        self.canvas.create_image(self.width/2, self.height/2, image=self.image_backgound)

        if self.inSubScreen:
            self.drawSongBalls()
            if (time.time() - self.startTime) % 1 > 0.5:    # make pointer flash
                self.pointerPos = (100, 100)
                self.canvas.create_image(self.pointerPos, image=self.image_pointer)
            self.canvas.create_text(360, 100,
                                    text="Click on a flashing circle to start!",
                                    font="Helvetica 26 bold")
            if self.onPlay:
                self.canvas.create_text(300, 150,
                        text=self.onPlay.name + " selected.\nMake sure you have its wav file.",
                        font="Helvetica 20")
                self.nextArrowPos = (self.width/2, 340)
                self.canvas.create_image(self.nextArrowPos,
                                         image=self.image_next)
        if self.inAudScreen:
            if (time.time() - self.startTime) % 1 > 0.5:   # make pointer flash
                self.pointerPos = (100, 100)
                self.canvas.create_image(self.pointerPos, image=self.image_pointer)
            self.canvas.create_text(self.width/2, 100,
                            text="Load this song's wave file by clicking this.",
                            font="Helvetica 26 bold")
            self.canvas.create_image(self.loadPos, image=self.image_load)
            if self.isProcessing:
                self.drawProcessing()

        if self.inAnimationScreen:
            # static content
            note = "Color of our algorithm's result is blue. Reference is red."
            self.canvas.create_text(20, 40, text=note, font="Helvetica 16",
                                    anchor=SW)

            currentTime = time.time()
            elapsedTime = currentTime - self.animationStartTime
            # print "elapsed time:", elapsedTime
            self.canvas.create_window(30, 60, window=self.textWidget,
                                      anchor=NW, height=40, width=920)
            self.canvas.create_window(30, 130, window=self.textWidgetRef,
                                      anchor=NW, height=40, width=920)
            self.textWidget.config(font="Helvetica 26")
            self.textWidgetRef.config(font="Helvetica 26")

            # find line
            for i in range(len(self.lyrics)):
                line = self.lyrics[i]
                start = line[0]
                content = line[1]
                if i == len(self.lyrics) - 1:
                    if elapsedTime > start:
                        self.currentContent = content
                        self.lineNumber = i
                        break
                else:
                    nextLine = self.lyrics[i + 1]
                    nextStart = nextLine[0]
                    if elapsedTime > start and elapsedTime < nextStart:
                        self.currentContent = content
                        self.lineNumber = i
                        break

            # find word
            for j in range(len(self.stamps[self.lineNumber])):
                word = self.stamps[self.lineNumber][j]
                start = word[0]
                index = word[1]
                if j == len(self.stamps[self.lineNumber]) - 1:
                    if elapsedTime > start:
                        print index
                        print self.currentContent.split()
                        self.currentWord = self.currentContent.split()[index]
                else:
                    nextWord = self.stamps[self.lineNumber][j + 1]
                    nextStart = nextWord[0]
                    if elapsedTime > start and elapsedTime < nextStart:
                        self.currentWord = self.currentContent.split()[index]
                        break

            # color for result
            # self.red = random.randint(0, 255)
            # self.green = random.randint(0, 255)

            blue = int(time.time() % 255)
            specialColor = self.rgbString(self.red, self.green, blue)

            self.textWidget.config(state=NORMAL)
            self.textWidget.delete(1.0, END)
            self.textWidget.insert(END, self.currentContent)
            self.textWidget.tag_configure("current", foreground="blue")
            self.textWidget.highlight_pattern(self.currentWord, "current")
            self.textWidget.config(state=DISABLED)


            # find reference word
            for j in range(len(self.references[self.lineNumber])):
                word = self.references[self.lineNumber][j]
                if len(word):
                    start = word[0]
                    index = word[1]
                    if j == len(self.references[self.lineNumber]) - 1:
                        if elapsedTime > start:
                            self.currentWordRef = \
                                self.currentContent.split()[index]
                            break
                    else:
                        nextWord = self.references[self.lineNumber][j + 1]
                        nextStart = nextWord[0]
                        if elapsedTime > start and elapsedTime < nextStart:
                            self.currentWordRef =\
                                self.currentContent.split()[index]
                            break

            # color for result
            self.textWidgetRef.config(state=NORMAL)
            self.textWidgetRef.delete(1.0, END)
            self.textWidgetRef.insert(END, self.currentContent)
            self.textWidgetRef.tag_configure("current", foreground="red")
            self.textWidgetRef.highlight_pattern(self.currentWordRef, "current")
            self.textWidgetRef.config(state=DISABLED)



    def drawProcessing(self):
        self.canvas.create_text(300, 220, text="Processing...",
                                font="Helvetica 20")

    def drawSongBalls(self):
        for i in range(len(self.posSongBalls)):
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = int(time.time() % 255)
            color = self.rgbString(red, green, blue)
            self.canvas.create_oval(self.posSongBalls[i], width=0, fill=color)


    def setSongBalls(self, number):
        for i in range(number):
            cx = random.random() * (self.width - 30)
            cy = random.random() * (self.height - 15)
            r = 10000
            while (cx-r < 0)or(cy-r < 0)or(cx+r > self.width)or(cy+r > self.height):
                r = random.random() * 50 + 5
                cx = random.random() * (self.width - 30)
                cy = random.random() * (self.height - 15)
            self.posSongBalls.append((cx-r, cy-r, cx+r, cy+r))

    @staticmethod
    def rgbString(red, green, blue):
        return "#%02x%02x%02x" % (red, green, blue)

if __name__ == '__main__':
    Visualization().run()
