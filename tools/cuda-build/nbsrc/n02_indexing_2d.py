from notebooks import md, code

NB = {'file': '02-thread-indexing-2d.ipynb', 'title': '2D grids: one thread per pixel',
      'intro': '''
This notebook goes with chapter 2.2 (thread indexing) and chapter 5.3 (stencils).
You will launch a 2D grid of 2D blocks, give each thread one pixel of an image, turn a colour image into grey,
and then blur it with a 3 × 3 box filter. Every result is checked against NumPy.

Run it in Google Colab with a T4 GPU. Without a GPU, set NUMBA_ENABLE_CUDASIM=1 before the first import to use the slow simulator.
''', 'cells': [
    code('''
import os
import math
import numpy as np
from numba import cuda

SIM = os.environ.get("NUMBA_ENABLE_CUDASIM") == "1"
H, W = (24, 40) if SIM else (2160, 3840)
print("image size:", H, "rows by", W, "columns")
''', {1: 'Reads the environment variable that turns on the simulator.',
      2: 'ceil, to round the number of blocks up.',
      3: 'NumPy arrays hold the image on the CPU.',
      4: 'The Numba CUDA compiler.',
      6: 'True when we run in the simulator.',
      7: 'A 4K frame on a real GPU (3840 × 2160 pixels), a tiny image in the simulator so it finishes quickly.',
      8: 'Shows the size. Rows come first, like in NumPy: image[row, column].'}),
    md('''
## 1. A colour test image

We build the image in NumPy so the notebook needs no files. Shape (H, W, 3) means H rows, W columns, and 3 colour
values (red, green, blue) per pixel, each from 0 to 255.
'''),
    code('''
rng = np.random.default_rng(0)
img = rng.integers(0, 256, size=(H, W, 3), dtype=np.uint8)
img[: H // 2, : W // 2] = (255, 0, 0)
print(img.shape, img.dtype, "top left pixel:", img[0, 0])
''', {1: 'A random number generator with a fixed seed, so every run gives the same image.',
      2: 'Random colours. uint8 is one byte per value, the usual format for photos.',
      3: 'Paint the top left quarter pure red, so we have a part where we know the answer.',
      4: 'Shape (H, W, 3), type uint8, and the first pixel, which is (255, 0, 0).'}),
    md('''
## 2. The grey scale kernel

Grey = 0.299 R + 0.587 G + 0.114 B. These weights follow how bright each colour looks to the human eye.
cuda.grid(2) returns two numbers: the global x (column) and the global y (row) of this thread.
'''),
    code('''
@cuda.jit
def to_gray(rgb, gray):
    x, y = cuda.grid(2)
    if y < gray.shape[0] and x < gray.shape[1]:
        r = rgb[y, x, 0]
        g = rgb[y, x, 1]
        b = rgb[y, x, 2]
        gray[y, x] = 0.299 * r + 0.587 * g + 0.114 * b
''', {1: 'Compile the next function as a GPU kernel.',
      2: 'Input image of shape (H, W, 3) and output of shape (H, W).',
      3: 'x = blockIdx.x × blockDim.x + threadIdx.x and y the same with .y. x walks along a row, y walks down the rows.',
      4: 'Bounds check in both directions. The last row and column of blocks stick out past the image.',
      5: 'Red value of pixel (y, x). Row first, then column, then channel.',
      6: 'Green value.',
      7: 'Blue value.',
      8: 'Weighted sum, written to the matching pixel of the output. Each thread writes only its own pixel.'}),
    code('''
d_rgb = cuda.to_device(img)
d_gray = cuda.device_array((H, W), dtype=np.float32)

block = (16, 16)
grid = (math.ceil(W / block[0]), math.ceil(H / block[1]))
to_gray[grid, block](d_rgb, d_gray)
gray = d_gray.copy_to_host()

ref = img @ np.array([0.299, 0.587, 0.114])
print("grid:", grid, "blocks of", block, "threads")
print("matches NumPy:", np.allclose(gray, ref, atol=1e-3))
print("red corner grey value:", gray[0, 0], "expected", 0.299 * 255)
''', {1: 'Copy the image to the GPU.',
      2: 'Space for the grey image on the GPU, one float per pixel.',
      4: '16 × 16 = 256 threads per block. The first number is x (columns), the second is y (rows).',
      5: 'Blocks along x cover the width W, blocks along y cover the height H. Note the order: x first, then y.',
      6: 'Launch the 2D grid of 2D blocks.',
      7: 'Copy the grey image back to the CPU.',
      9: 'The same formula in NumPy: a matrix product of each pixel\'s 3 values with the 3 weights.',
      10: 'How many blocks we launched in each direction.',
      11: 'Compare with NumPy. atol allows for small float rounding.',
      12: 'The red corner should be 0.299 × 255 = 76.2.'}),
    md('''
## 3. A 3 × 3 box blur (a stencil)

Each output pixel is the mean of the 3 × 3 pixels around it. Pixels on the border use only the neighbours that exist.
Every input pixel is read by up to 9 threads, which is why chapter 5.3 loads a tile into shared memory first.
'''),
    code('''
@cuda.jit
def blur3(src, dst):
    x, y = cuda.grid(2)
    h, w = src.shape
    if y >= h or x >= w:
        return
    total = 0.0
    count = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            yy = y + dy
            xx = x + dx
            if 0 <= yy < h and 0 <= xx < w:
                total += src[yy, xx]
                count += 1
    dst[y, x] = total / count
''', {1: 'Compile as a kernel.',
      2: 'Input grey image and output blurred image.',
      3: 'This thread\'s pixel: column x and row y.',
      4: 'Image height and width, read from the array shape.',
      5: 'Threads outside the image have no pixel.',
      6: 'So they stop at once. Returning early is fine here because this kernel has no __syncthreads.',
      7: 'Running sum of the neighbours.',
      8: 'How many neighbours were inside the image. Corners have 4, edges 6, the inside 9.',
      9: 'Row offsets -1, 0, +1.',
      10: 'Column offsets -1, 0, +1.',
      11: 'Row of the neighbour.',
      12: 'Column of the neighbour.',
      13: 'Skip neighbours that fall outside the image.',
      14: 'Add the neighbour to the sum. This is the global memory read that shared memory tiling would save.',
      15: 'Count it.',
      16: 'The mean, written to this thread\'s own output pixel.'}),
    code('''
d_blur = cuda.device_array_like(d_gray)
blur3[grid, block](d_gray, d_blur)
blur = d_blur.copy_to_host()

pad = np.pad(gray, 1)
ones = np.pad(np.ones_like(gray), 1)
s = sum(pad[1 + dy : 1 + dy + H, 1 + dx : 1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
c = sum(ones[1 + dy : 1 + dy + H, 1 + dx : 1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
print("blur matches NumPy:", np.allclose(blur, s / c, atol=1e-3))
''', {1: 'An output array on the GPU with the same shape and type as the grey image.',
      2: 'Launch with the same grid and block shape as before.',
      3: 'Copy the result back.',
      5: 'NumPy check. Pad the image with a ring of zeros so every pixel has 9 neighbours.',
      6: 'A padded image of ones, used to count how many real neighbours each pixel has.',
      7: 'Sum of the 9 shifted copies of the image gives the neighbour sum for every pixel at once.',
      8: 'The same sums over the ones give the neighbour count.',
      9: 'Mean = sum ÷ count, compared with the GPU result.'}),
    md('''
## 4. Try these

1. Swap the order and write grid = (ceil(H / 16), ceil(W / 16)). Run it with a non square image and explain what breaks.
2. Use blocks of (32, 8) and (8, 32). Which one gives coalesced reads in to_gray, and why (chapter 3.2)?
3. Count the global reads per output pixel of blur3. Then work out how many reads a 16 × 16 tile with a 1 pixel halo needs (chapter 5.3).
'''),
]}
