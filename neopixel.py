import random
import sys
import threading
import time
import wx

class Frame(wx.Frame):
    def __init__(self, parent, title, strip):
        self._size = 8
        self._pad = 8
        self._width = 400
        self._height = 200
        self._xjitter = [6 * random.random() for _ in xrange(strip.numPixels())]
        self._yjitter = [6 * random.random() for _ in xrange(strip.numPixels())]

        wx.Frame.__init__(self, parent, title=title, size=(self._width, self._height))
        # TODO: update width/height on window resize
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)

        self._strip = strip

        self.Centre()
        self.Show()

    def center(self, i):
        row_size = (self._width - self._pad) / (2 * self._size + self._pad)
        col = i % row_size
        row = i / row_size

        if row % 2 == 1:
            col = row_size - col - 1

        a = self._pad + self._size
        b = a + self._size
        jx = self._xjitter[i]
        jy = self._yjitter[i]

        return (a + b * col + jx, a + b * row + jy)

    def OnPaint(self, e):
        start = time.time()
        use_gc = True

        if use_gc:
            dc = wx.GCDC(wx.PaintDC(self))
        else:
            dc = wx.PaintDC(self)

        pixels = self._strip.getDisplayed()

        # Draw string
        for i in xrange(1,len(pixels)):
            x1, y1 = self.center(i-1)
            x2, y2 = self.center(i)
            dc.DrawLine(x1, y1, x2, y2)

        # Draw lights in a second pass so they are on top.
        for i, c in enumerate(pixels):
            dc.SetBrush(wx.Brush(c))
            x, y = self.center(i)
            dc.DrawCircle(x, y, self._size)

        if use_gc:
            self.Refresh()

        print("time: ", time.time() - start)

    def OnClick(self, e):
        wx.App.Get().ExitMainLoop()
        sys.exit()

    def redraw():


class Simulation(threading.Thread):
    def __init__(self, strip):
        threading.Thread.__init__(self)
        self._strip = strip
        self._initialized = False

    def run(self):
        self._app = wx.App(clearSigInt=False)
        self._frame = Frame(None, 'Test', strip=self._strip)
        self._initialized = True
        self._app.MainLoop()

    def update(self):
        if not self._initialized:
            return
        self._frame.redraw()
        wx.PostEvent(self._frame, wx.PaintEvent()) 

def Color(red, green, blue, white=0):
    return (white << 24) | (red << 16) | (green << 8) | blue

class Adafruit_NeoPixel(object):
    def __init__(self, num, *args):
        """A simulated neopixel strip.

        Args:
            num: the number of lights in the strip
            *args: the rest of the args are ignored, but allowed for
                compatibility with the neopixel library
        """
        self._buffer = [0] * num
        self._displayed = [wx.Colour(0,0,0)] * num
        self._lock = threading.Lock()

    def begin(self):
        self._sim = Simulation(self)
        self._sim.start()

    def show(self):
        """Updates display with pixel data"""
        with self._lock:
            self._displayed = [
                wx.Colour((c >> 16) & 0xff,
                          (c >> 8) & 0xff,
                          c & 0xff)
                for c in self._buffer
            ]
        self._sim.update()

    def setPixelColor(self, n, color):
        self._buffer[n] = color

    def setPixelColorRGB(self, n, red, green, blue, white=0):
        self.setPixelColor(n, Color(red, green, blue, white))

    def getPixels(self):
        return self._buffer.copy()

    def numPixels(self):
        return len(self._buffer)

    def getPixelColor(self, n):
        return self._buffer[n]

    def getDisplayed(self):
        """Gets the array of displayed pixel data."""
        with self._lock:
            return self._displayed

class ws(object):
  SK6812_STRIP_RGBW = 0
  SK6812W_STRIP = 1
