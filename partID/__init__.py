"""
Contains main function -- majority of heavy lifting

TODO
    Flat is better than nested...
"""

import cv2
import numpy as np

from .draw import diagram_line
from .rects import combine_rects
from .threads import (find_threads,
                      max_contours,
                      thread_pts,
                      thresh_image)
from .utils import modAreaRect, rects_before_square


def main(img):
    plots = []

    # Threshold image and combine largest bounding rectangles.
    can = thresh_image(img, gaus=True)
    cont_can, conts = max_contours(can, largest=40)
    rects = np.asarray(map(cv2.boundingRect, conts))
    rect_pts = np.asarray([[(x, y), (x + w, y + h)] for x, y, w, h in rects])
    combined_rects = combine_rects(rect_pts, miss=10)

    plot_cont = cont_can.copy()
    for rect in rect_pts:
        cv2.rectangle(plot_cont, pt1=tuple(rect[0]), pt2=tuple(rect[1]),
                      color=255, thickness=5)
    plots.append(plot_cont)

    sorted_rects = rects_before_square(combined_rects)
    part_rect = sorted_rects[0]
    quarter_rect = sorted_rects[-1]

    qcenter = quarter_rect.mean(0).round().astype(int)
    qdiameter = np.diff(quarter_rect, axis=0).mean().round().astype(int)
    cv2.circle(img, center=tuple(qcenter), radius=qdiameter / 2,
               color=(0, 0, 255), thickness=5)

    left, top, right, bottom = part_rect.flatten()
    part_can = cont_can[top:bottom, left:right]

    plot_cont = cont_can.copy()
    for rect in combined_rects:
        cv2.rectangle(plot_cont, pt1=tuple(rect[0]), pt2=tuple(rect[1]),
                      color=255, thickness=5)
    plots.append(plot_cont)

    # Find rotation angle of part then rotate image
    r255, c255 = np.where(part_can > 0)
    pts255 = np.vstack((r255 + top, c255 + left))
    rcenter, (rwidth, rheight), angle = modAreaRect(pts255.T)
    box = cv2.boxPoints((rcenter, (rwidth, rheight), angle))
    plot_cont = cont_can.copy()
    cv2.drawContours(plot_cont, contours=[np.int0(box)], contourIdx=0,
                     color=255, thickness=5)
    plots.append(plot_cont)

    M = cv2.getRotationMatrix2D(rcenter, angle=angle + 90, scale=1)
    rot_can = cv2.warpAffine(cont_can, M, dsize=cont_can.shape[::-1])
    rot_img = cv2.warpAffine(img, M, dsize=cont_can.shape[::-1])
    rot_plt = cv2.warpAffine(plot_cont, M, dsize=cont_can.shape[::-1])
    plots.append(rot_plt)

    loX, loY = rcenter[0] - rheight / 2, rcenter[1] - rwidth / 2
    hiX, hiY = rcenter[0] + rheight / 2, rcenter[1] + rwidth / 2
    part_can = rot_can[loY:hiY, loX:hiX]
    part_img = rot_img[loY:hiY, loX:hiX]
    # plots.append(np.pad(part_can, 100, 'constant'))
    # plots.append(np.pad(outline(part_can, 5), 100, 'constant'))
    top_part = part_can[:part_can.shape[0] / 5]
    L_max = top_part.argmax(1).min()
    R_max = top_part.shape[1] - np.fliplr(top_part).argmax(1).min()
    head_diff = R_max - L_max

    toleft = loX - 50
    diagram_line(rot_img, (toleft, loY), (toleft, hiY))  # Part height
    above = loY - 150
    diagram_line(rot_img, (L_max + loX, above), (R_max + loX, above),
                 horizontal=True)
    # plots.append(rot_img)
    # diagram_line(rot_img, (loX, above), (hiX, above),
    #              horizontal=True)  # Part width
    # return 0, plots

    all_dists = []
    for side in ['left', 'right']:
        t_lo, t_hi = find_threads(part_can)
        threads_can = part_can[t_lo:t_hi]
        threads_img = part_img[t_lo:t_hi]
        for peak, pts in zip(['max', 'min'], thread_pts(threads_can)):
            if side == 'right':
                pts[:, 0] = threads_can.shape[1] - pts[:, 0]
            coord_diffs = np.diff(pts, axis=0)
            pt_dists = np.linalg.norm(coord_diffs, axis=1)
            all_dists = np.concatenate((all_dists, pt_dists))
            for pt in pts:
                if peak == 'max':
                    cv2.circle(threads_img, tuple(pt), 2, (0, 128, 255), 5)
                else:
                    cv2.circle(threads_img, tuple(pt), 2, (0, 0, 255), 5)
        if side == 'left':
            part_can = np.fliplr(part_can)

    IN_PER_QUARTER_DIAMETER = 0.955
    px_per_in = qdiameter / IN_PER_QUARTER_DIAMETER
    threads_per_in = px_per_in / np.median(all_dists)
    head_size = head_diff / px_per_in
    part_height, part_width = np.asarray(part_can.shape) / px_per_in

    output = {
        'diameter': 'Diameter: {:d} px'.format(qdiameter),
        'thread': 'Thread: {:.0f} TPI'.format(threads_per_in),
        'head size': 'Head Size: {:.2f} in'.format(head_size),
        'height': 'Height: {:.2f} in'.format(part_height),
        'width': 'Width: {:.2f} in'.format(part_width),
    }
    for i, text in enumerate(output.values()):  # Draw results on top left of image
        print(text)
        cv2.putText(rot_img, text=text, org=(100, 125 + i * 100),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=2,
                    color=(0, 0, 0), thickness=4)
    plots.append(rot_img)
    return output, plots
