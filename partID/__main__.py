#!/usr/bin/env python3

import os
import sys

import cv2
from six.moves.urllib.request import urlretrieve

from partID import main


files = sys.argv[1:]

def write_img(img, filename, output_dir='output/'):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    output = os.path.join(output_dir, filename)
    cv2.imwrite(output, img)


for filename in files:
    print(filename)

    if filename.startswith('http'):
        path, _ = urlretrieve(filename)
        img = cv2.imread(path)
        os.remove(path)
    else:
        img = cv2.imread(filename)

    output = main(img)

    for description in output.values():
        print(description)
