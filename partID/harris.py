#!/usr/bin/env python2

import cv2
import numpy as np
from sys import argv

script, filename = argv

img = cv2.imread(filename)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

gray = np.float32(gray)
dst = cv2.cornerHarris(gray, 2, 3, 0.04)
dst = cv2.dilate(dst,None)

def binsearch(grid, lo, hi, goal):
    mdpt = (lo+hi)/2
    if lo >= hi:
        return mdpt
    mdpt_val = len( np.where(grid > mdpt)[0] )
    if 0.95*goal < mdpt_val < 1.05*goal:
        return mdpt
    if mdpt_val < goal:
        return binsearch(grid, lo, mdpt, goal)
    else:
        return binsearch(grid, mdpt, hi, goal)

def findthresh(grid, goal=1000):
    upper = goal / 10
    lower = -upper
    goal = goal*1000
    lower = lower*1000
    upper = upper*1000
    mdpt_mean = np.mean(grid)
    len_mean = len(np.where(grid > mdpt_mean)[0])
    if len_mean < goal:
        return binsearch(grid, lower, mdpt_mean, goal)
    else:
        return binsearch(grid, mdpt_mean, upper, goal)

goal = 2 * len(dst) * len(dst[0]) / 32
thresh = findthresh(dst, goal / 1000)
pts = np.where( dst > thresh )
print len(pts[0])
img[pts] = [0, 0, 255]




filename = filename.split('/')
filename = filename[len(filename) - 1]

out = 'harris_' + filename
cv2.imwrite(out, img)

