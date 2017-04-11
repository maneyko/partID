"""
Contains main function -- majority of heavy lifting.
"""

import cv2
import numpy as np

from . import draw
from . import rects
from . import threads
from . import thresholding
from . import utils


def get_shapes(img):
    """
    Returns contoured version of `img`, bounding rectangle of the part,
    and quarter.
    """
    thresh = thresholding.gaussian(img)
    draw.save(thresh)
    contoured, contours = utils.max_contours(thresh, largest=40)
    draw.save(contoured)
    bounding_rects = np.asarray([cv2.boundingRect(c) for c in contours])
    rect_pts = np.asarray([[(x, y), (x + w, y + h)]
                           for x, y, w, h in bounding_rects])
    draw.save(draw.plot_rectangles(contoured.copy(), rect_pts))
    combined = rects.combine_rects(rect_pts, miss=10)
    sorted_rects = rects.before_square(combined)
    part_rect = sorted_rects[0]
    quarter_rect = sorted_rects[-1]
    draw.save(draw.plot_rectangles(contoured.copy(), [part_rect, quarter_rect]))
    return contoured, part_rect, quarter_rect


def rotate(img, part, coords):
    """
    Parameters
    ----------
    img : ndarray
        Image to rotate.
    part : ndarray
        Black and white part of image to rotate `img` about.
    coords : ndarray
        Top left and bottom right coordinates of `shape`.

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

    left, top = center[0] - height // 2, center[1] - width // 2
    right, bottom = center[0] + height // 2, center[1] + width // 2
    part_rect = np.asarray([[left, top], [right, bottom]])

    return rotated_img, part_rect


def main(img):
    """
    Main function that performs all analysis on `img`.

    Steps
    -----
    * Create contoured image.
    * Locate bounding rectangles for part and quarter.
    * Rotate image about the part.
    * Locate threads in upper portion of image.
    * Calculate distances between peaks and troughs of threads.
    """
    contoured, part_rect, quarter_rect = get_shapes(img)

    quarter_diameter = np.diff(quarter_rect, axis=0).mean()

    left, top, right, bottom = part_rect.ravel()
    part_contour = contoured[top:bottom, left:right]

    rotated_img, part_coords = rotate(contoured, part_contour, part_rect)
    draw.save(draw.plot_rectangles(rotated_img.copy(), [part_coords]))
    left, top, right, bottom = part_coords.ravel()
    part = rotated_img[top:bottom, left:right]
    draw.save(part)

    all_dists = threads.distances(part)

    IN_PER_QUARTER_DIAMETER = 0.955
    px_per_in = quarter_diameter / IN_PER_QUARTER_DIAMETER
    threads_per_in = px_per_in / np.median(all_dists)
    part_height, part_width = np.asarray(part.shape) / px_per_in

    output = {
        'diameter': 'Quarter Diameter: {:.0f} px'.format(quarter_diameter),
        'thread': 'Thread: {:.0f} TPI'.format(threads_per_in),
        'height': 'Height: {:.2f} in'.format(part_height),
        'width': 'Width: {:.2f} in'.format(part_width),
    }
    return output
