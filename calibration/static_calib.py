import cv2 as cv
import numpy as np
import datetime
import os
from csv import writer as csv_write
from pathlib import Path

key = { 0 : 'chessboard', #built-in chessboard detection
        1 : 'harris', #harris corner
        2 : 'shitomashi'} #shi-tomashi corner

time_now = str(datetime.datetime.now())

def main():
    cboard = cv.imread('23-11_finecamimage.PNG')

    #using built in chessboard corner detection
    retval0, corners0 = cv.findChessboardCorners(cboard, (9, 8), None)
    fnl0 = cv.drawChessboardCorners(cboard, (9, 8), corners0, retval0)
    
    # #using harris corner detection
    # cboard_harris = cv.imread('calib_square_v9a.jpg')
    # gray_cboard = cv.cvtColor(cboard,cv.COLOR_BGR2GRAY)
    # gray_cboard = np.float32(gray_cboard)
    # dst = cv.cornerHarris(gray_cboard,2,3,0.04)
    # #result is dilated for marking the corners, not important
    # dst = cv.dilate(dst,None)
    # # Threshold for an optimal value, it may vary depending on the image.
    # cboard_harris[dst>0.01*dst.max()]=[0,0,255]

    # #using shi-tomashi corner detection


    while True:
        cv.imshow('corner detects', fnl0)
        if cv.waitKey(1) == ord('q'):
            break

    cv.destroyAllWindows()
    save(corners0, retval0, fnl0, key[0])

def save(corner_coords, return_val, img, key):
    data_folder = Path(__file__).parent / 'data'
    data_filename = str(key) + '_corner_points_'+ time_now
    data_file = data_folder / data_filename 

    data_folder = Path(__file__).parent / 'data'
    img_suffix = '.png'
    img_filename = str(key) + '_picture_' + time_now + img_suffix
    img_file = data_folder / img_filename

    print('Saving coordinates in file: '+str(data_file))
    
    with open(data_file, 'a') as file:
        if return_val:
            for x in corner_coords:
                writer = csv_write(file)
                writer.writerow([x]) 
            cv.imwrite(str(img_file), img)
    
    if return_val:
        trans_rot_calc(data_file)


def trans_rot_calc(coords_file):
    with open(str(coords_file), 'r') as file:
        for x in file:
            pass
             
if __name__ == "__main__":
    main()