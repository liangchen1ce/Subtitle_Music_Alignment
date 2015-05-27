# This class is from post:
# http://stackoverflow.com/questions/3781670/how-to-highlight-text-in-a-tkinter-text-widget
from Tkinter import *

class CustomText(Text):
    '''A text widget with a new method, highlight_pattern()

    example:

    text = CustomText()
    text.tag_configure("red", foreground="#ff0000")
    text.highlight_pattern("this should be red", "red")

    The highlight_pattern method is a simplified python
    version of the tcl code at http://wiki.tcl.tk/3246
    '''
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        '''Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression.
        '''

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit",
                                count=count, regexp=regexp)

            if index == "": break
            temp = index + "+1c"
            # (m, n) = temp.split(".")
            # digit = int(m) + float(int(n))/10
            indexSpace = self.search(" ", temp, stopindex=END)
            if len(indexSpace) != 0:  # pattern is not the last word
                a = int(index.split(".")[-1])
                b = int(indexSpace.split(".")[-1])
                if a + len(pattern) != b: break  # pattern is not a word
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")