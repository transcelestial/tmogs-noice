import numpy as np
import cv2 as cv
from pathlib import Path
from csv import writer as csv_write
import sys
import datetime
import argparse

start_time = datetime.datetime.now()

#filename = 'slanted_mini.PNG'
filename = 'calib_square_v12_rot.png'
#filename = '23-11_finecamimage3.PNG'
img = cv.imread(filename)
img = cv.cvtColor(img,cv.COLOR_BGR2GRAY)

retval0, corners0 = cv.findChessboardCorners(img, (9, 8), None)
fnl0 = cv.drawChessboardCorners(img, (9, 8), corners0, retval0)

# #using harris corner detection
# cboard_harris = cv.imread(filename)
# gray_cboard = cv.cvtColor(cboard_harris,cv.COLOR_BGR2GRAY)
# gray_cboard = np.float32(gray_cboard)
# dst = cv.cornerHarris(gray_cboard,2,3,0.04)
# #result is dilated for marking the corners, not important
# dst = cv.dilate(dst,None)
# # Threshold for an optimal value, it may vary depending on the image.
# cboard_harris[dst>0.01*dst.max()]=[0,0,255]

while True:
    cv.imshow('corner detects', fnl0)
    if cv.waitKey(1) == ord('q'):
        break

cv.destroyAllWindows()