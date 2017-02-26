#!/usr/bin/env python

import os

import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt

def move_forward(data, lower, upper, move, min_len=1):
    """
    Moves on data until there are no pts between `upper` and `lower`.
    """
    inc = 0
    while inc + move < data.size:
        forward = data[inc : inc + move]
        between = np.where((lower < forward) & (forward < upper))[0]
        if between.size > min_len - 1:
            inc += move
        else:
            break
    return data[:inc]

def filter_first(grid, axis=0, dist=1):
    """Returns first white pixel on a side of `grid`."""
    side = grid.argmax(axis)
    if dist < 2:
        return np.intc(side)
    filt = medfilt(side, dist)
    return np.intc(filt)

def find_threads(can, filter_dist=1):
    """Returns top portion of an image that is likely to be threads.

    `filter_first` is used on the left side of `can`, then the median
    of the first portion of the result is taken. That median is used to
    move forward on the image until there are no points that intersect
    the median. The distance moved is used as the lower bound returned.
    """
    filt = filter_first(can, axis=1, dist=5)
    lo = filt.size * 3 / 100
    hi = lo * 6
    med = np.median(filt[lo:hi])
    before_med = np.where((med - 10 < filt) & (filt < med + 10))[0][0]
    tr_filt = filt[before_med:]

    first_move = move = tr_filt.size / 25
    spread = 0.05
    lower, upper = med * (1 - spread), med * (1 + spread)
    for _ in range(10):
        moved = move_forward(tr_filt, lower, upper, move)
        if moved.size > 2 * move:
            break
        move += first_move / 2
    bottom_cut = before_med + moved.size
    return before_med, bottom_cut

def thread_pts(threads_can):
    """Returns the thread coordinates (in px) of a canny image.

    It is assumed that the image is cut so that only to part is in
    the frame and that the threads are at the top of the image.
    """
    threads = filter_first(threads_can, axis=1, dist=5)
    line = np.median(threads)
    above = np.where(threads < line)[0]
    below = np.where(threads > line)[0]
    peak_pts = []
    for peak in [above, below]:
        diffs = np.diff(peak)
        jumps = np.where(diffs > 1)[0] + 1
        hills = np.split(peak, jumps)
        mdpts = np.intc(map(np.median, hills)).reshape(-1, 1)
        mdiffs = np.diff(mdpts, axis=0)
        too_big = np.where(mdiffs > np.median(mdiffs) * 3 / 2)[0]
        if too_big.size:
            if too_big[0] > mdpts.size/2:
                mdpts = mdpts[:too_big[0]]
        peak_pts.append(np.hstack((threads[mdpts], mdpts)))
    return peak_pts

def thresh_image(img, blur_size=5, canlow=50, canhigh=100, threshold=-1,
                 equ=False, gaus=False):
    """Custom thresholding function that performs different filters.

    Parameters
    ----------
    img : array_like
        Image as numpy array
    blur_size : int
        Applys `cv2.GaussianBlur` with
    """
    if len(img.shape) > 2:  # Accept a color image and a gray image
        gray = cv2.cvtColor(img, code=cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    if threshold > 0:
        return cv2.Canny(gray, threshold1=threshold, threshold2=threshold)
    blur = cv2.GaussianBlur(gray, ksize=(blur_size, blur_size), sigmaX=0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    ret_equ = clahe.apply(blur)
    if equ:
        return ret_equ
    if gaus:
        return cv2.adaptiveThreshold(ret_equ,
                maxValue=255,
                adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                thresholdType=cv2.THRESH_BINARY_INV,
                blockSize=101,
                C=2)
    else:
        return cv2.Canny(ret_equ, threshold1=canlow, threshold2=canhigh)
    return can


def max_contours(thresh, largest=10):
    """
    Takes `largest` contours of an image, then draws them on a new
    image.
    """
    _, thresh_contours, hierarchy = \
            cv2.findContours(thresh, mode=cv2.RETR_TREE,
                             method=cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(thresh,
                     contours=thresh_contours,
                     contourIdx=-1,
                     color=255,
                     thickness=4)
    thresh_blank = np.zeros(thresh.shape)
    contours = np.asarray([cv2.approxPolyDP(cont, epsilon=3, closed=True)
                           for cont in thresh_contours])
    areas = np.asarray(map(cv2.contourArea, contours))
    top_areas = areas.argsort()[-largest:]
    top_conts = contours[top_areas]
    for cont in top_conts:
        cv2.drawContours(thresh_blank, contours=[cont], contourIdx=0,
                         color=255, thickness=3, maxLevel=0)
    return thresh_blank, top_conts
