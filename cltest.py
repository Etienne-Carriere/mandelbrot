import pyopencl as cl
import numpy as np

ctx = cl.create_some_context(interactive=False)
queue = cl.CommandQueue(ctx)

prg = cl.Program(ctx, """
__kernel void test(__global int* out, const int sizeX, const int sizeY) {
    unsigned int x = get_global_id(0);
    unsigned int y = get_global_id(1);
    out[x*sizeX + y] = x+y;
}
""").build()

mf = cl.mem_flags

a = np.ascontiguousarray(np.ones((10, 10), dtype=np.int32))
abuf = cl.Buffer(ctx, mf.WRITE_ONLY, a.nbytes)

prg.test(queue, a.shape, None, abuf, np.int32(10), np.int32(10))

print(a)

cl.enqueue_copy(queue, a, abuf).wait()
print()
print()

print(a)
