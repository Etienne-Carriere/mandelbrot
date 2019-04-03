import threading
import functools
import pyopencl as cl
import numpy as np
import math
import time
import cv2

platform = cl.get_platforms()[0]
print(platform.get_devices())

ctx = cl.create_some_context(interactive = False)
queue = cl.CommandQueue(ctx)

def readProgram(filename):
    lines = open(filename, 'r').read()
    prg = cl.Program(ctx, lines).build()
    return prg

mf = cl.mem_flags
# SIZE = 600
XSIZE, YSIZE = 2000, 2000
XDSIZE, YDSIZE = XSIZE, YSIZE
STEPSIZE = 100 # WASD step size
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


def main():
    global s, p, zoom, iters, precision, cx, cy, renderTime, root, c, oldi, timeText, itk, oldThread
    s = 0.0
    p = 0.0
    zoom = 512
    iters = 32
    precision = 0
    cx, cy = 0.3306736862509997, 0.42686190053779904
    while True:
        # calculatedImage = calcFrac()
        a = time.time()
        calcFracCL()
        renderTime = time.time() - a
        img = cv2.cvtColor(imgarr, cv2.COLOR_HSV2BGR)
        cv2.imshow('float', img)
        key = cv2.waitKey(0)
        if key == 86: # page up
            zoom = int(zoom / 2)
            if zoom == 0:
                zoom = 1
            # iters = math.pow((math.log(zoom, 2) * 3), 1.8)
        elif key == 85: # page down
            zoom *= 2
            # iters = math.pow((math.log(zoom, 2) * 3), 1.8)
        elif key == 82: # up arrow
            iters *= 2
        elif key == 84: # down arrow
            if iters >= 2:
                iters /= 2
        elif key == 119: # 'w'
            cx -= (STEPSIZE / zoom)
        elif key == 115: # s
            cx += (STEPSIZE / zoom)
        elif key == 97: # a
            cy -= (STEPSIZE / zoom)
        elif key == 100: # d
            cy += (STEPSIZE / zoom)
        elif key == 102: # f
            precision += 1
            precision %= 2
        elif key == 'Left':
            s += 0.01
        elif key == 'Right':
            s -= 0.01
        elif key == 'End':
            p += 0.01
        elif key == 'Home':
            p -= 0.01
        else:
            print(key)
        print('Iters:%i Zoom:%i Center:(%f,%f) Precision:%i s:%f Render Time:%f' % (iters, zoom, cx, cy, precision, s, renderTime))

if __name__ == '__main__':
    try:
        main()
    finally:
        abuf.release()
