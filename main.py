#!/usr/bin/env python

import sys
import time

import cv2

from partID.draw import tplot
from partID import main


start = time.time()
files = sys.argv[1:]

for filename in files:

    tplot.name = filename
    print(filename)

    img = cv2.imread(filename)
    height, width, _ = img.shape
    if height < width:
        img = cv2.transpose(img)

    now = time.time()
    output, plots = main(img)
    print('Main: {:.3f}'.format(time.time() - now))

    for i, p in enumerate(plots):
        tplot(p, '_{:d}'.format(i), img=True)


print('Total: {:.3f}'.format(time.time() - start))
