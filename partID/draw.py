"""
Drawing and plotting functions
"""

import os

import cv2
import matplotlib.pyplot as plt

from .threads import filter_first


def tplot(fig, name='', lines='', pts=False, clear=True,
          lim=0, llim=0, img=False, output=True):
    """Helper function for making fast plots

    Parameters
    ----------
    fig : array_like
        Data to plot
    name : str
        Value to append to `tplot.outfile`
    """
    if hasattr(tplot, 'name'):
        base = os.path.basename(tplot.name)
        tplot.outfile = base[:base.find('.')]  # Basename without extension
    else:
        return
    if output:
        if not os.path.exists('output/'):
            os.mkdir('output/')
        write = 'output/{}{}.jpg'.format(tplot.outfile, name)
    if img:
        cv2.imwrite(write, fig)
        return
    if lines and lim < 0:
        return
    if lines:
        clear = False
        if lines == 'v':
            plt.plot([fig, fig], [llim, lim])
        elif lines == 'h':
            plt.plot([llim, lim], [fig, fig])
    elif pts:
        plt.scatter(range(len(fig)), fig)
    else:
        plt.plot(range(len(fig)), fig)
    if clear:
        plt.savefig(write)
        plt.clf()
        plt.cla()


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
