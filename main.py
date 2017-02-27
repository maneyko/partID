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
    height, width = img.shape[:2]
    if height < width:
        img = cv2.transpose(img)

    before_main = time.time()
    output, plots = main(img)
    print('Main: {:.3f}'.format(time.time() - before_main))

    for i, p in enumerate(plots):
        tplot(p, name='_{:d}'.format(i), img=True)


print('Total: {:.3f}'.format(time.time() - start))
