from tkinter import Tk, Canvas
import threading
import functools
from PIL import Image, ImageTk
import pyopencl as cl
import numpy as np
import math
import time

platform = cl.get_platforms()[0]
print(platform.get_devices())

ctx = cl.create_some_context(interactive = True)
queue = cl.CommandQueue(ctx)

def readProgram(filename):
    lines = open(filename, 'r').read()
    prg = cl.Program(ctx, lines).build()
    return prg

mf = cl.mem_flags
# SIZE = 600
XSIZE, YSIZE = 2000, 2000
XDSIZE, YDSIZE = XSIZE, YSIZE
# XDSIZE, YDSIZE = XSIZE, YSIZE
#a = np.ascontiguousarray(np.ones((600, 600), dtype=np.int32) * -1, dtype=np.int32)
a = np.ascontiguousarray(np.ones((XSIZE, YSIZE), dtype=np.int32) * -1)
abuf = cl.Buffer(ctx, mf.WRITE_ONLY, a.nbytes)
imgarr = np.ascontiguousarray(np.ndarray((XSIZE, YSIZE, 3), dtype=np.uint8))
imgbuf = cl.Buffer(ctx, mf.WRITE_ONLY, imgarr.nbytes)

prg = readProgram("mandelbrot.cl")

def getPix(x, y):
    c = ()
    while abs(z) < 2 and iters < 10:
        z = z**2 + c
        iters += 1
    print(a)
    return iters

def normalize():
    mx = 0
    mn = iters + 2
    for row in a:
        for col in row:
            mn = min(mn, col)
            mx = max(mx, col)
    print (mn, mx)
    norm = lambda a: (a - mn) * (255 / (mx - mn))
    for x in range(XSIZE):
        for y in range(YSIZE):
            a[x][y] = norm(a[x][y])

def calcFracCL():
    if precision == 0:
        prg.pixel32(queue, a.shape, None, abuf, np.float32(cx), np.float32(cy), np.int64(zoom), np.int32(iters), np.float32(s), np.float32(p), np.int32(XSIZE), np.int32(YSIZE)).wait()
    elif precision == 1:
        prg.pixel64(queue, a.shape, None, abuf, np.float64(cx), np.float64(cy), np.int64(zoom), np.int32(iters), np.float32(s), np.float32(p), np.int32(XSIZE), np.int32(YSIZE)).wait()
    else:
        prg.pixelHighPrecision(queue, a.shape, None, abuf, np.float64(cx), np.float64(cy), np.int64(zoom), np.int32(iters)).wait()
    # cl.enqueue_read_buffer(queue, abuf, a).wait()
    cl.enqueue_copy(queue, a, abuf).wait()
    min, max = a.min(), a.max()
    prg.color(queue, imgarr.shape, None, imgbuf, abuf, np.int32(min), np.int32(max), np.int32(XSIZE), np.int32(YSIZE))
    # cl.enqueue_read_buffer(queue, imgbuf, imgarr).wait()
    cl.enqueue_copy(queue, imgarr, imgbuf).wait()

def fracHighPrecision():
    prg.pixelHighPrecision(queue, a.shape, None, abuf, np.float64(cx), np.float64(cy), np.int64(zoom), np.int32(iters)).wait()
    l

def calcFrac():
    global renderTime
    s = time.time()
    calcFracCL()
    e = time.time()
    renderTime = e-s
##    print(e-s)
##    normalize()
    i = Image.fromarray(imgarr, 'HSV').convert('RGB')
    i = i.resize((XDSIZE, YDSIZE), Image.ANTIALIAS)
    #i.save('tmp.png')
    return i

def changeZoom(evt):
    global zoom, iters, cx, cy, precision, itk, oldi, s, p, oldThread, calculatedImage
    if evt.keysym == 'Next':
        zoom = int(zoom / 2)
        if zoom == 0:
            zoom = 1
        # iters = math.pow((math.log(zoom, 2) * 3), 1.8)
    if evt.keysym == 'Prior':
        zoom *= 2
        # iters = math.pow((math.log(zoom, 2) * 3), 1.8)
    if evt.keysym == 'Up':
        iters *= 2
    if evt.keysym == 'Down':
        if iters >= 2:
            iters /= 2
    if evt.keysym == 'w':
        cx -= (50 / zoom)
    if evt.keysym == 's':
        cx += (50 / zoom)
    if evt.keysym == 'a':
        cy -= (50 / zoom)
    if evt.keysym == 'd':
        cy += (50 / zoom)
    if evt.keysym == 'f':
        precision += 1
        precision %= 2
    if evt.keysym == 'Left':
        s += 0.01
    if evt.keysym == 'Right':
        s -= 0.01
    if evt.keysym == 'End':
        p += 0.01
    if evt.keysym == 'Home':
        p -= 0.01
    print('Iters:%i Zoom:%i Center:(%f,%f) Precision:%i s:%f' % (iters, zoom, cx, cy, precision, s))
    # if oldThread is not None:
    #     oldThread.join()
    # oldThread = threading.Thread(target=otherThread)
    # oldThread.start()
    calculatedImage = calcFrac()
    root.after(1, updateCanvas)

def otherThread():
    global calculatedImage
    calculatedImage = calcFrac()
    root.after(1, updateCanvas)
    print("THREAD DOME")

def updateCanvas():
    global itk, c, oldi, root, calculatedImage
    itk = ImageTk.PhotoImage(image=calculatedImage)
    c.delete(oldi)
    oldi = c.create_image(XDSIZE/2, YDSIZE/2, image=itk)
    c.itemconfig(timeText, text=str(round(renderTime * 1000)) + "ms")
    c.lift(timeText)
    # c.update()

def main():
    global s, p, zoom, iters, precision, cx, cy, renderTime, root, c, oldi, timeText, itk, oldThread
    s = 0.0
    p = 0.0
    zoom = 512
    iters = 32
    precision = 0
    cx, cy = 0.3306736862509997, 0.42686190053779904
    renderTime = 0
    oldThread = None
    root = Tk()
    root.title("float")
    root.bind("<KeyPress>", changeZoom)
    c = Canvas(root, width=XDSIZE, height=YDSIZE)
    c.pack()
    itk = ImageTk.PhotoImage(image = calcFrac())
    oldi = c.create_image(XSIZE/2, YSIZE/2, image=itk)
    timeText = c.create_text(550, 50, text=str(round(renderTime * 1000)) + "ms", fill="#1111CC")
    t = 0
    calcFrac()
    print(a)
    try:
        root.mainloop()
    finally:
        abuf.release()

if __name__ == '__main__':
    main()
