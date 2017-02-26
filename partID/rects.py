"""
Rectangle wrangling
"""

import numpy as np


def runion(rect1, rect2, miss=0):
    """Checks if rectangles overlap."""
    if np.array_equal(rect1, rect2):
        return False
    a = np.absolute(np.subtract(rect1, rect2)) - miss
    d1 = np.diff(rect1, axis=0)
    d2 = np.diff(rect2, axis=0)
    if np.greater(a, d1).any() and np.greater(a, d2).any():
        return False
    return True


def rjoin(rect1, rect2):
    """Joins two rectangles."""
    stacked = np.vstack((rect1, rect2))
    lo_coord = np.amin(stacked, 0)
    hi_coord = np.amax(stacked, 0)
    return np.asarray([lo_coord, hi_coord])


def minmax_pts(rect):
    """Formats rectangle points."""
    lo = np.min(rect, axis=0)
    hi = np.max(rect, axis=0)
    return np.vstack((lo, hi))


def combine_rects(rects, miss=0):
    """Joins all overlapping rectangles.

    If there is a difference of `miss` between any two points on two
    rectangles they are considered overlapping.
    """
    rects = np.asarray(map(minmax_pts, rects))
    for _ in range(len(rects)):
        bool_joins = np.asarray([runion(rects[0], rect, miss=miss)
                                 for rect in rects])
        nojoin = np.where(bool_joins == False)[0]
        tojoin = np.where(bool_joins)[0]
        for rect in rects[[tojoin]]:
            # Change the base rectangle to overlapping results.
            rects[0] = rjoin(rects[0], rect)
        rects = rects[[nojoin]]
        rects = np.roll(rects, -1, 0)
    return rects
