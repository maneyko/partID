"""
Helper functions
"""

import numpy as np
import cv2

def modAreaRect(pts):
    """Fixes angle orientation issues with `cv2.minAreaRect.`

    Has same API as `cv2.minAreaRect`
    """
    rcenter, (rwidth, rheight), angle = cv2.minAreaRect(pts)
    rcenter = np.intc(rcenter[::-1])  # Change to row, column order
    angle = -1 * (angle + 90)
    if rwidth < rheight:
        angle -= 90
        rwidth, rheight = rheight, rwidth
    return tuple(rcenter), tuple(np.intc([rwidth,rheight])), angle


def rects_before_square(rects, diff=0.1):
    """
    Returns a sorted array of rectangles up to and including a square.
    """
    if rects.shape[0] == 1:
        return rects
    lens = np.diff(rects, axis=1).squeeze()
    ratios = (lens[:, 0] / np.float_(lens[:, 1])).flatten()
    asort_idx = np.prod(lens, axis=1).argsort(axis=0)
    rsort = rects[asort_idx[::-1]]
    ratios = ratios[asort_idx[::-1]]
    q_ind = np.argmax((1-diff < ratios) & (ratios < 1+diff))
    return rsort[:q_ind+1]
