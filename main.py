#!/usr/bin/env python3

import os
import sys
import time

import cv2

from partID import main


start = time.time()
files = sys.argv[1:]

def write_img(img, basename, output_dir='output/'):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    output = os.path.join(output_dir, basename)
    cv2.imwrite(img, output)


for filename in files:
    print(filename)

    img = cv2.imread(filename)

    before_main = time.time()
    output, plots = main(img)
    print('Main: {:.3f}'.format(time.time() - before_main))

    basename = os.path.basename(filename)
    for i, plot in enumerate(plots):
        write_img(plot, '{}_{:02d}.jpg'.format(
                         basename[:basename.find('.')], i))
    for description in output.values():
        print(description)
