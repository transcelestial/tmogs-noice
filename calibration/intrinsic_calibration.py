import cv2
import numpy as np
import os
import glob
import math

# Extracting path of individual image stored in a given directory CHANGE THIS TO THE PATH WITH THE PNGs
images = glob.glob('./calibration_images_nfov/*.png')

# known camera properties
known_plate_scale = 6.8742 # radians per pixel
imx296_pixel_size = 3.4e-06
imx219_pixel_size = 1.12e-06
preset_dist = 32.8 #in m

# Defining the dimensions of checkerboard
CHECKERBOARD = (7,4)
real_square_l = 0.0054 # in m
total_length = real_square_l * (CHECKERBOARD[0] - 1)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Creating vector to store vectors of 3D points for each checkerboard image
objpoints = []
# Creating vector to store vectors of 2D points for each checkerboard image
imgpoints = [] 
imgpoints2 = []

# Defining the world coordinates for 3D points
objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
prev_img_shape = None

num = 1

for fname in images:
    print('reading {}'.format(fname))
    img = cv2.imread(fname)
    #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    # If desired number of corners are found in the image then ret = true
    ret, corners = cv2.findChessboardCorners(img, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
    img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners, ret)

    if ret == True:
        objpoints.append(objp)
        imgpoints.append(corners)
        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners, ret)
    """
    If desired number of corner are detected,
    we refine the pixel coordinates and display 
    them on the images of checker board
    """
    # #sub pixel
    # if ret == True:
    #     objpoints.append(objp)
    #     # refining pixel coordinates for given 2d points.
    #     corners2 = cv2.cornerSubPix(img, corners, (5,5),(-1,-1), criteria)
         
    #     imgpoints.append(corners2)
 
    #     # Draw and display the corners
    #     img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
    
    # # calculating plate scale 
    # x_distance = corners[0][0][0] - corners[CHECKERBOARD[0] - 1][0][0]
    # y_distance = corners[0][0][1] - corners[CHECKERBOARD[0] - 1][0][1]
    # pixel_length = math.sqrt((x_distance)**2 + (y_distance)**2)
    # distance = total_length/math.tan(known_plate_scale*pixel_length)
    # print('distance of image ' + str(num) + ' = ' + str(distance) + 'mm')
    # length_range = (math.atan(total_length / distance))
    # radians_per_pixel = length_range/pixel_length
    # print('radians per pixel: ', radians_per_pixel)

    # cv2.imshow('img',img)
    # cv2.waitKey(0)

    print(str(num) + " images processed...")
    num += 1
cv2.destroyAllWindows()
 
h,w = img.shape[:2]
# print('checkerboard corners: ')
# print(corners)

"""
Performing camera calibration by 
passing the value of known 3D points (objpoints)
and corresponding pixel coordinates of the 
detected corners (imgpoints)
"""
# print("objpoints: \n")
# print(objpoints)
print("calculating output...")
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (img.shape[0], img.shape[1]), None, None)
rot_mat = []
for vector in rvecs:
    rot_mat.append(cv2.Rodrigues(vector))

mean_error = 0

for i in range(len(objpoints)):
    projectpoints, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    imgpoints2.append(projectpoints)
    error = cv2.norm(imgpoints[i], projectpoints, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error

print("total mean error: " + str(mean_error/len(objpoints)))

focal_length_px = (mtx[0][0] + mtx[1][1])/2 #in pixels
print('camera focal length (px): ' + str(focal_length_px))
focal_length_m = focal_length_px * imx296_pixel_size
print('camera focal length (m): ' + str(focal_length_m))
x_distance_px = imgpoints[0][0][0][0] - imgpoints[0][CHECKERBOARD[0] - 1][0][0]
y_distance_px = imgpoints[0][0][0][1] - imgpoints[0][CHECKERBOARD[0] - 1][0][1]
checkerboard_row_px = math.sqrt((x_distance_px)**2 + (y_distance_px)**2)
print('projected row length (px): ' + str(checkerboard_row_px))
checkerboard_row_m = checkerboard_row_px * imx296_pixel_size
print('projected row length (m): ' + str(checkerboard_row_m))

x_distance_px_projected = imgpoints2[0][0][0][0] - imgpoints2[0][CHECKERBOARD[0] - 1][0][0]
y_distance_px_projected = imgpoints2[0][0][0][1] - imgpoints2[0][CHECKERBOARD[0] - 1][0][1]
checkerboard_row_px_projected = math.sqrt((x_distance_px_projected)**2 + (y_distance_px_projected)**2)
print('projected row length 2 (px): ' + str(checkerboard_row_px_projected))
checkerboard_row_m_projected = checkerboard_row_px_projected * imx296_pixel_size
print('projected row length 2 (m): ' + str(checkerboard_row_m_projected))

checkerboard_row_m_actual = real_square_l *(CHECKERBOARD[0] - 1)
print('actual row length: ' + str(checkerboard_row_m_actual))

print('preset distance: {}'.format(preset_dist))
distance = focal_length_m * (checkerboard_row_m_actual/checkerboard_row_m) - focal_length_m
print('theoretical distance: ' + str(distance))
distance = focal_length_m * (checkerboard_row_m_actual/checkerboard_row_m_projected) - focal_length_m
print('theoretical distance 2: ' + str(distance))

focal_angle_px = ((math.atan(checkerboard_row_m_actual/(preset_dist+focal_length_m)))/checkerboard_row_px)*180/(math.pi)
print('angle per pixel (degrees): {}'.format(focal_angle_px))

print("Camera matrix : \n")
print(mtx)
# print("dist : \n")
# print(dist)
# print("rvecs : \n")
# print(rvecs)

# print("rot matrices : \n")
# print(rot_mat)

# print("tvecs : \n")
# print(tvecs)

