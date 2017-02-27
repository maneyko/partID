#!/usr/bin/env python

import sys
import time

import cv2
import numpy as np

def print_circles(img, circles):
    global outfile
    a, b, c = circles.shape
    for i in range(1):
        cv2.circle(img, (circles[0][i][0], circles[0][i][1]),
                   circles[0][i][2], (0, 0, 255), 3)
        cv2.circle(img, (circles[0][i][0], circles[0][i][1]),
                   2, (0, 255, 0), 3)  # Draw center of circle
    cv2.imwrite('zcircles_' + outfile + '.jpg', img)

def find_circles(img, radius, step, lower=-1):
    if lower < 0:
        lower = step
    circles = None
    while circles is None and lower < radius:
        circles = \
            cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=1,
                             minDist=len(img) / 2, circles=np.array([]),
                             param1=100, param2=50, minRadius=radius - step,
                             maxRadius=radius)
        radius -= step
    return circles, radius+step

def theshold_image(gray):
    global outfile
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    equ = clahe.apply(blur)
    can = cv2.Canny(equ, 50, 100)
    # gaus = cv2.adaptiveThreshold(equ, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #         cv2.THRESH_BINARY_INV, 11, 2)

    return can

def find_quarter(filename):
    global outfile
    img = cv2.imread(filename, 1)
    cimg = img.copy()
    outfile = filename.split('/')[-1].split('.')[0]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    canny = theshold_image(gray)
    print np.mean(canny)
    cv2.imwrite( 'canny_' + outfile + '.jpg', canny)
    return 0


if __name__ == '__main__':
    now = time.time()
    for f in sys.argv[1:]:
        print(f)
        try:
            radius = find_quarter(f)
        except AttributeError:
            print('ERROR')
            continue
    print(time.time() - now)

