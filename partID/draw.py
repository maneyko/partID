"""
Drawing and plotting functions
"""

import os
import glob

import cv2


def save(img, output_dir='output', extension='jpg'):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    files = glob.glob(os.path.join(os.path.realpath(output_dir), '*'))
    name = '{:02d}.{}'.format(len(files), extension)
    output = os.path.join(os.path.realpath(output_dir), name)
    cv2.imwrite(output, img)


def plot_rectangles(gray, rects):
    for rect in rects:
        cv2.rectangle(gray, pt1=tuple(rect[0]), pt2=tuple(rect[1]),
                      color=255, thickness=5)
    return gray


def diagram_line(img, lo, hi, width=10, end_len=50, color=0,
                 horizontal=False):
    """
    Draws a "fancy" line on the image.

    Example: |-------------------|

    Parameters
    ----------
    img : ndarray
        Image on which to draw the line
    lo : array_like
        Coordinates on `img` of lower point
    hi : array_like
        Coordinates on `img` of higher point
    width : int
        Thickness of line
    end_len : int
        Length (in pixels) of perpendicular mini-lines
    color : int
        Grayscale color of line
    horizontal : bool
    """
    if horizontal:
        idx = 1
    else:
        idx = 0
    if lo[idx] - end_len // 2 > 0:
        end = lo[idx] - end_len
    else:
        end = 2
    if horizontal:
        pts = [
            ((lo[0] + width // 2, lo[1]),
                (hi[0] - width // 2, hi[1])),
            ((lo[0] + width // 2, end),
                (lo[0] + width // 2, lo[1] + end_len // 2)),
            ((hi[0] - width // 2, end),
                (hi[0] - width // 2, hi[1] + end_len // 2))
        ]
    else:
        pts = [
            ((lo[0], lo[1] + width // 2),
                (hi[0], hi[1] - width // 2)),
            ((end, lo[1] + width // 2),
                (lo[0] + end_len // 2, lo[1] + width // 2)),
            ((end, hi[1] - width // 2),
                (lo[0] + end_len // 2, hi[1] - width // 2))
        ]
    for pt1, pt2 in pts:
        cv2.line(img, pt1, pt2, color=color, thickness=width)
    return img
