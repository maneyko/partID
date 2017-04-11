"""
General utility functions.
"""

import numpy as np
import cv2


def modAreaRect(pts):
    """Fixes angle orientation issues with `cv2.minAreaRect.`

    Has same API as `cv2.minAreaRect`.
    """
    rcenter, (rwidth, rheight), angle = cv2.minAreaRect(pts)
    rcenter = np.intc(rcenter[::-1])  # Change to row, column order
    angle = -1 * (angle + 90)
    if rwidth < rheight:
        angle -= 90
        rwidth, rheight = rheight, rwidth
    return tuple(rcenter), tuple(np.intc([rwidth,rheight])), angle


def max_contours(gray, largest=10):
    """
    Takes `largest` contours of an image, then draws them on the
    returned image.

    Parameters
    ----------
    gray : ndarray
        Black and white image.
    largest : int
        Number of largest contours to draw on reurned image.

    Returns
    -------
    contoured : ndarray
        Image with `largest` contours drawn.
    top_conts : ndarray
        Contours that have been drawn.
    """
    _, contours, hierarchy = \
            cv2.findContours(gray, mode=cv2.RETR_TREE,
                             method=cv2.CHAIN_APPROX_SIMPLE)

    # **For demo**
    cv2.drawContours(gray, contours=contours, contourIdx=-1,
                     color=255, thickness=4)

    contoured = np.zeros(gray.shape)
    approx_curves = np.asarray([cv2.approxPolyDP(cont, epsilon=3, closed=True)
                                for cont in contours])
    areas = np.asarray([cv2.contourArea(c) for c in approx_curves])
    top_areas = areas.argsort()[-largest:]
    top_conts = approx_curves[top_areas]
    for cont in top_conts:
        cv2.drawContours(contoured, contours=[cont], contourIdx=0,
                         color=255, thickness=3, maxLevel=0)
    return contoured, top_conts
