#!/usr/bin/env python3

import os
import sys
import time

import cv2

from partID import main


files = sys.argv[1:]

def write_img(img, filename, output_dir='output/'):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    output = os.path.join(output_dir, filename)
    cv2.imwrite(output, img)


for filename in files:
    print(filename)

    img = cv2.imread(filename)

    before_main = time.time()
    output = main(img)
    print('Main: {:.3f}'.format(time.time() - before_main))

    for description in output.values():
        print(description)
