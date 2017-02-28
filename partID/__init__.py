"""
Contains main function -- majority of heavy lifting

TODO
    Flat is better than nested...
"""

import cv2
import numpy as np

from . import draw
from . import rects
from . import threads
from . import thresholding
from . import utils


def plot_rectangles(gray, rects):
    for rect in rects:
        cv2.rectangle(gray, pt1=tuple(rect[0]), pt2=tuple(rect[1]),
                      color=255, thickness=5)
    return gray


def get_shapes(img):
    thresh = thresholding.gaussian(img)
    contoured, contours = utils.max_contours(thresh, largest=40)
    bounding_rects = np.asarray([cv2.boundingRect(c) for c in contours])
    rect_pts = np.asarray([[(x, y), (x + w, y + h)]
                           for x, y, w, h in bounding_rects])
    combined = rects.combine_rects(rect_pts, miss=10)
    sorted_rects = rects.before_square(combined)
    part_rect = sorted_rects[0]
    quarter_rect = sorted_rects[-1]
    return contoured, part_rect, quarter_rect


def rotate(img, part, coords):
    """
    Parameters
    ----------
    img : ndarray
        Image to rotate
    part : ndarray
        Black and white part of image to rotate `img` about
    coords : ndarray
        Top left and bottom right coordinates of `shape`

    Returns
    -------
    rotated_img : ndarray
    rotated_part : ndarray
    """
    left, top, right, bottom = coords.ravel()
    y_pts, x_pts = np.where(part > 0)
    pts = np.vstack((y_pts + top, x_pts + left))

    center, (width, height), angle = utils.modAreaRect(pts.T)
    box = cv2.boxPoints((center, (width, height), angle))
    M = cv2.getRotationMatrix2D(center, angle=angle + 90, scale=1)
    rotated_img = cv2.warpAffine(img, M, dsize=img.shape[::-1][:2])

    loX, loY = center[0] - height // 2, center[1] - width // 2
    hiX, hiY = center[0] + height // 2, center[1] + width // 2
    rotated_part = rotated_img[loY:hiY, loX:hiX]

    return rotated_img, rotated_part


def main(img):
    plots = []
    contoured, part_rect, quarter_rect = get_shapes(img)

    qcenter = quarter_rect.mean(0).round().astype(int)
    qdiameter = np.diff(quarter_rect, axis=0).mean().round().astype(int)

    left, top, right, bottom = part_rect.ravel()
    part_cont = contoured[top:bottom, left:right]

    rotated_img, part = rotate(contoured, part_cont, part_rect)

    all_dists = threads.distances(part)

    IN_PER_QUARTER_DIAMETER = 0.955
    px_per_in = qdiameter / IN_PER_QUARTER_DIAMETER
    threads_per_in = px_per_in / np.median(all_dists)
    part_height, part_width = np.asarray(part.shape) / px_per_in

    output = {
        'diameter': 'Diameter: {:d} px'.format(qdiameter),
        'thread': 'Thread: {:.0f} TPI'.format(threads_per_in),
        'height': 'Height: {:.2f} in'.format(part_height),
        'width': 'Width: {:.2f} in'.format(part_width),
    }
    return output, plots
