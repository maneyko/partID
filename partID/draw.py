"""
Drawing and plotting functions
"""

import os

import cv2


def diagram_line(img, lo, hi, width=10, end_len=50, color=0,
                 horizontal=False):
    """
    Draws a "fancy" line on the image.

    Example: |-------------------|
    """
    if horizontal:
        endT = lo[1] - end_len // 2 if lo[1] - end_len // 2 > 0 else 2
        cv2.line(img,
                 pt1=(lo[0] + width // 2, lo[1]),
                 pt2=(hi[0] - width // 2, hi[1]),
                 color=0,
                 thickness=width)
        cv2.line(img,
                 pt1=(lo[0] + width // 2, endT),
                 pt2=(lo[0] + width // 2, lo[1] + end_len // 2),
                 color=color,
                 thickness=width)
        cv2.line(img,
                 pt1=(hi[0] - width // 2, endT),
                 pt2=(hi[0] - width // 2, hi[1] + end_len // 2),
                 color=color,
                 thickness=width)
    else:
        endL = lo[0] - end_len // 2 if lo[0] - end_len // 2 > 0 else 2
        cv2.line(img,
                 pt1=(lo[0], lo[1] + width // 2),
                 pt2=(hi[0], hi[1] - width // 2),
                 color=0,
                 thickness=width)
        cv2.line(img,
                 pt1=(endL, lo[1] + width // 2),
                 pt2=(lo[0] + end_len // 2, lo[1] + width // 2),
                 color=color,
                 thickness=width)
        cv2.line(img,
                 pt1=(endL, hi[1] - width // 2),
                 pt2=(lo[0] + end_len // 2, hi[1] - width // 2),
                 color=color,
                 thickness=width)
