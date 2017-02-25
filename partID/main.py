# vim: tw=100
# develop branch

import sys

import cv2
import numpy as np

from threads import (filter_first,
                     find_threads,
                     tplot,
                     thread_pts,
                     thresh_image)


def combine_rects(rects, miss=0):
    """Joins all overlapping rectangles.

    If there is a difference of `miss` between any two points on two
    rectangles they are considered overlapping.
    """

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


def diagram_line(img, lo, hi, width=10, end_len=50, color=0,
                 horizontal=False):
    """Draws a "fancy" line on the image.

    Example: |-------------------|
    """
    if horizontal:
        endT = lo[1] - end_len / 2 if lo[1] - end_len / 2 > 0 else 2
        cv2.line(img,
                 pt1=(lo[0] + width / 2, lo[1]),
                 pt2=(hi[0] - width / 2, hi[1]),
                 color=0,
                 thickness=width)
        cv2.line(img,
                 pt1=(lo[0] + width / 2, endT),
                 pt2=(lo[0] + width / 2, lo[1] + end_len/2),
                 color=color,
                 thickness=width)
        cv2.line(img,
                 pt1=(hi[0] - width / 2, endT),
                 pt2=(hi[0] - width / 2, hi[1] + end_len / 2),
                 color=color,
                 thickness=width)
    else:
        endL = lo[0] - end_len / 2 if lo[0] - end_len / 2 > 0 else 2
        cv2.line(img,
                 pt1=(lo[0], lo[1] + width / 2),
                 pt2=(hi[0], hi[1] - width / 2),
                 color=0,
                 thickness=width)
        cv2.line(img,
                 pt1=(endL, lo[1] + width / 2),
                 pt2=(lo[0] + end_len / 2, lo[1] + width / 2),
                 color=color,
                 thickness=width)
        cv2.line(img,
                 pt1=(endL, hi[1] - width / 2),
                 pt2=(lo[0] + end_len / 2, hi[1] - width / 2),
                 color=color,
                 thickness=width)


def max_contours(thresh, largest=10):
    """
    Takes `largest` contours of an image, then draws them on a new
    image.
    """
    _, thresh_contours, hierarchy = cv2.findContours(thresh, mode=cv2.RETR_TREE,
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


def modAreaRect(pts):
    """Fixes angle orientation issues with `cv2.minAreaRect.`"""
    rcenter, (rwidth, rheight), angle = cv2.minAreaRect(pts)
    rcenter = np.intc(rcenter[::-1])  # Change to row, column order
    angle = -(angle + 90)
    if rwidth < rheight:
        angle -= 90
        rwidth, rheight = rheight, rwidth
    return tuple(rcenter), tuple(np.intc([rwidth,rheight])), angle


def outline(grid, border=1, filt=5):
    """Outlines bordering points of `grid`."""
    height, width = grid.shape[:2]
    blank = np.zeros((height, width))
    left = filter_first(grid, axis=1, dist=filt)
    top = filter_first(grid, axis=0, dist=filt)
    right = width - 1 - filter_first(np.fliplr(grid), axis=1, dist=filt)
    bottom = height - 1 - filter_first(np.flipud(grid), axis=0, dist=filt)
    rangeh = np.arange(height)
    rangew = np.arange(width)
    for _ in range(border):
        try:
            blank[rangeh, left] = 255
            blank[rangeh, right] = 255
            blank[top, rangew] = 255
            blank[bottom, rangew] = 255
        except IndexError:
            break
        left += 1
        right -= 1
        top += 1
        bottom -= 1
    return blank


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

def main(img):
    plots = []

    # Threshold image and combine largest bounding rectangles.
    can = thresh_image(img, gaus=True)
    cont_can, conts = max_contours(can, largest=40)
    rects = np.asarray(map(cv2.boundingRect, conts))
    rect_pts = np.asarray([ [(x,y), (x+w,y+h)] for x, y, w, h in rects ])
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
    pts255 = np.vstack((r255+top, c255+left))
    rcenter, (rwidth, rheight), angle = modAreaRect(pts255.T)
    box = cv2.boxPoints((rcenter, (rwidth,rheight), angle))
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
    diagram_line(rot_img, (L_max + loX, above), (R_max + loX, above), horizontal=True)
    # plots.append(rot_img)
    # diagram_line(rot_img, (loX,above), (hiX,above), horizontal=True)  # Part width
    # return 0, plots

    """
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
                    cv2.circle(threads_img, tuple(pt), 2, (0,128,255), 5)
                else:
                    cv2.circle(threads_img, tuple(pt), 2, (0,0,255), 5)
        if side == 'left':
            part_can = np.fliplr(part_can)
    """

    IN_PER_QUARTER_DIAMETER = 0.955
    px_per_in = qdiameter / IN_PER_QUARTER_DIAMETER
    # threads_per_in = px_per_in / np.median(all_dists)
    head_size = head_diff / px_per_in
    part_height, part_width = np.asarray(part_can.shape) / px_per_in

    output = {
        'diameter': 'Diameter: {:d} px'.format(qdiameter),
        # 'thread': 'Thread: {:.0f} TPI'.format(threads_per_in),
        'head size': 'Head Size: {:.2f} in'.format(head_size),
        'height': 'Height: {:.2f} in'.format(part_height),
        'width': 'Width: {:.2f} in'.format(part_width),
    }
    for i, v in enumerate(output.values()):  # Draw results on top left of image
        print(v)
        cv2.putText(rot_img, text=v, org=(100, 125 + i * 100),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=2,
                    color=(0, 0, 0), thickness=4)
    plots.append(rot_img)
    return output, plots

if __name__ == '__main__':
    import time
    start = time.time()
    files = sys.argv[1:]
    for filename in files:
        tplot.name = filename
        print(filename)
        img = cv2.imread(filename)
        height, width, _ = img.shape
        if height < width:
            img = cv2.transpose(img)
        now = time.time()
        output, plots = main(img)
        print('Main: {:.3f}'.format(time.time() - now))
        for i, p in enumerate(plots):
            tplot(p, '_{:d}'.format(i), img=True)
    print('Total: {:.3f}'.format(time.time() - start))
