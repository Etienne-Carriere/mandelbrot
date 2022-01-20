#!/usr/bin/env python3
import threading
import functools
import pyopencl as cl
import numpy as np
import math
import time
import cv2

# There's so many global variables I hate it
print(cl.get_platforms())
platform = cl.get_platforms()[1]
print(platform.get_devices())

ctx = cl.Context(devices=platform.get_devices())
queue = cl.CommandQueue(ctx)

def readProgram(filename):
    lines = open(filename, 'r').read()
    prg = cl.Program(ctx, lines).build()
    return prg

mf = cl.mem_flags
XSIZE, YSIZE = 2000, 2000
XDSIZE, YDSIZE = XSIZE, YSIZE
STEPSIZE = 100 # WASD step size
a = np.ascontiguousarray(np.ones((XSIZE, YSIZE), dtype=np.int32) * -1)
abuf = cl.Buffer(ctx, mf.WRITE_ONLY, a.nbytes)
imgarr = np.ascontiguousarray(np.ndarray((XSIZE, YSIZE, 3), dtype=np.uint8))
imgbuf = cl.Buffer(ctx, mf.WRITE_ONLY, imgarr.nbytes)

prg = readProgram("mandelbrot.cl")

def calcFracCL():
    if precision == 0:
        prg.pixel32(queue, a.shape, None, abuf, np.float32(cx), np.float32(cy), np.int64(zoom), np.int32(iters), np.float32(s), np.float32(p), np.int32(XSIZE), np.int32(YSIZE)).wait()
    elif precision == 1:
        prg.pixel64(queue, a.shape, None, abuf, np.float64(cx), np.float64(cy), np.int64(zoom), np.int32(iters), np.float32(s), np.float32(p), np.int32(XSIZE), np.int32(YSIZE)).wait()
    cl.enqueue_copy(queue, a, abuf).wait()
    min, max = a.min(), a.max()
    prg.color(queue, imgarr.shape, None, imgbuf, abuf, np.int32(min), np.int32(max), np.int32(XSIZE), np.int32(YSIZE))
    cl.enqueue_copy(queue, imgarr, imgbuf).wait()

def main():
    global s, p, zoom, iters, precision, cx, cy, renderTime, root, c, oldi, timeText, itk, oldThread
    s = 0.0
    p = 0.0
    # Iters:524288 Zoom:8192 Center:(-0.670303,0.109479) Precision:0 s:0.000000 Render Time:6.550749
    zoom = 8192
    iters = 524288
    precision = 0
    cx, cy = -0.670303, 0.109479
    a = time.time()
    calcFracCL()
    renderTime = time.time() - a
    print('Iters:%i Zoom:%i Center:(%f,%f) Precision:%i s:%f Render Time:%f' % (iters, zoom, cx, cy, precision, s, renderTime))

if __name__ == '__main__':
    try:
        main()
    finally:
        abuf.release()
