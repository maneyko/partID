"""
Thresholding functions
"""

import cv2


def convert_gray(img):
    if len(img.shape) > 2:
        return cv2.cvtColor(img, code=cv2.COLOR_BGR2GRAY)
    return img


def equalize(img, blur_size=5):
    gray = convert_gray(img)
    blur = cv2.GaussianBlur(gray, ksize=(blur_size, blur_size), sigmaX=0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(blur)


def gaussian(img, method='ADAPTIVE_THRESH_GAUSSIAN_C',
             threshold_type='THRESH_BINARY_INV'):
    method = getattr(cv2, method)
    threshold_type = getattr(cv2, threshold_type)
    gray = convert_gray(img)
    equ = equalize(gray)
    return cv2.adaptiveThreshold(equ, maxValue=255, adaptiveMethod=method,
                                 thresholdType=threshold_type, blockSize=101,
                                 C=2)
