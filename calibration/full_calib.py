import numpy as np
import cv2 as cv
from pathlib import Path
from csv import writer as csv_write
import sys
import datetime
import argparse

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(
    description='First var: 0 for built in checkerboard detection, 1 for harris corner detection, 2 for sub pixel accuracy. Default is 0./n\
                Second var: 0 for using predefined png image, 1 for using fine camera, 2 for using coarse camera. Default is 0.')
ap.add_argument("algo", nargs='?', default=0, type=int,
                help="0 for built in checkerboard detection, 1 for harris corner detection, 2 for sub pixel accuracy. Default is 0.")
ap.add_argument("img", nargs='?', default=0, type=int,
                help="0 for using predefined png image, 1 for using fine camera, 2 for using coarse camera. Default is 0.")
args = vars(ap.parse_args())

start_time = datetime.datetime.now()
simple_corner_coords = []
refined_corner_coords = []

#declare save locations
data_folder = Path(__file__).parent / 'harris'
img_folder = data_folder / 'images'
mat_file = 'mat_corners.csv'
mat_file_path = data_folder / mat_file 

def reformat(img):
    if args["img"] == 0:
        gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    else:
        gray = cv.convertScaleAbs(img, alpha=0.25)
    print('test' + str(gray.shape))
    return gray

def img_set():
    if args["img"] == 0:
        #using predefined image
        filename = 'calib_square_7x4_rot5.png'
        img = cv.imread(filename)
        img = reformat(img)
        return img

    if args["img"] == 1:
        #using fine camera
        camera = cv.VideoCapture("/dev/video0", cv.CAP_V4L2)
        camera.set(cv.CAP_PROP_FOURCC,
                cv.VideoWriter_fourcc('Y', '1', '0', ' '))
        camera.set(cv.CAP_PROP_CONVERT_RGB, 0)
        camera.set(cv.CAP_PROP_FPS, 60)

        if not camera.isOpened():
            print("Cannot open camera")

        while True:
            ret, frame = camera.read()
            frame = reformat(frame)
            cv.imshow('Press any key to freeze frame', frame)
            if cv.waitKey(1) == ord('q'):
                print('1' + str(frame.shape))
                img = frame
                break
        print('2' + str(img.shape) )     
        return img
        
    if args["img"] == 2:
        #using coarse camera
        camera = cv.VideoCapture("/dev/video1", cv.CAP_V4L2)
        camera.set(cv.CAP_PROP_FOURCC,
                cv.VideoWriter_fourcc('Y', '1', '0', ' '))
        camera.set(cv.CAP_PROP_CONVERT_RGB, 0)
        camera.set(cv.CAP_PROP_FPS, 60)

        if not camera.isOpened():
            print("Cannot open camera")

        while True:
            ret, frame = camera.read()
            frame = reformat(frame)
            cv.imshow('Press any key to freeze frame', frame)
            if cv.waitKey(1) == ord('q'):
                break
        
        img = frame
        return img

def corner_detect(img):

    if args["algo"] == 0:
        #built in checkerboard detection
        retval0, corners0 = cv.findChessboardCorners(img, (7, 4), None)
        builtin_checkerboard_img = cv.drawChessboardCorners(img, (7, 4), corners0, retval0)
        print(retval0)
        for x in range(corners0.shape[0]):
            simple_corner_coords.append((corners0[x][0][0], corners0[x][0][1]))
        
        print('Saving corner coordinates in path: '+str(mat_file_path))
        with open(mat_file_path, 'w') as file:
            for x in simple_corner_coords:
                writer = csv_write(file)
                writer.writerow(x) 
        return builtin_checkerboard_img, corners0



    if args["algo"] == 1:
        # #harris corner detection
        # gray = cv.cvtColor(img,cv.COLOR_GRAY2BGR)
        # print(gray.shape)
        # ret,gray = cv.threshold(img,127,255,cv.THRESH_BINARY)
        # gray = cv.cvtColor(img,cv.COLOR_GRAY2BGR)
        # gray = np.float32(gray)
        # print(gray.shape)
        # dst = cv.cornerHarris(gray,2,3,0.04)

        #harris corner detection
        dst = cv.cornerHarris(img,2,3,0.04)

        # Threshold for an optimal value, it may vary depending on the image.
        mat = dst>0.01*dst.max()
        print('4' + str(img.shape))
        img = cv.cvtColor(img,cv.COLOR_GRAY2BGR)
        print('5' + str(img.shape))
        img[mat] = np.array([0, 0, 255])

        #look at mat, determine which points are rough corners
        for x in range(mat.shape[0]): #x of the mat, which is 793 if using 'calib_square_v11.png'
            for y in range(mat.shape[1]): #y of the mat, which is 1121 if using 'calib_square_v11.png'
                if (mat[x][y] == True).all():
                    simple_corner_coords.append((x,y))
        print(len(simple_corner_coords))
        # #check and output all pixels that are corners
        # for x in range(len(img)): #for normal harris
        #     for y in range(len(img[x])):
        #         if (img[x][y] == np.array([0, 0, 255])).all():
        #             simple_corner_coords.append((x,y))
        
        #prioritise top left corner of each cluster as reference point for next step
        for element in simple_corner_coords:
            x_element = element[0]
            y_element = element[1]
            if (x_element + 1, y_element) in simple_corner_coords:
                simple_corner_coords.remove((x_element + 1, y_element))
            if (x_element, y_element + 1) in simple_corner_coords:
                simple_corner_coords.remove((x_element, y_element + 1))
            if (x_element + 1, y_element + 1) in simple_corner_coords:
                simple_corner_coords.remove((x_element + 1, y_element + 1))

        print('Saving corner coordinates in path: '+str(mat_file_path))
        with open(mat_file_path, 'w') as file:
            for x in simple_corner_coords:
                writer = csv_write(file)
                writer.writerow(x) 

        return img, simple_corner_coords        


    if args["algo"] == 2:
        #harris corner detection
        ret,gray = cv.threshold(img,127,255,cv.THRESH_BINARY)
        gray = np.float32(gray)
        dst = cv.cornerHarris(gray,2,3,0.04)

        #only look at a window_size*window_size window around a point of interest to calculate the subpixel corner
        window_size = 6 #even number pls, >2 will be ideal i guess

        #sub pixel
        ret, dst_subpixel = cv.threshold(dst,0.01*dst.max(),255,0)
        dst_subpixel = np.uint8(dst_subpixel)

        # find centroids
        ret, labels, stats, centroids = cv.connectedComponentsWithStats(dst_subpixel)

        # define the criteria to stop and refine the corners
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.001)
        corners = cv.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)

        # Now draw them
        res = np.hstack((centroids,corners))
        res = np.int0(res)
        img_subpixel = cv.cvtColor(img,cv.COLOR_GRAY2BGR)
        img_subpixel[res[:,1],res[:,0]]=[0,0,255]
        img_subpixel[res[:,3],res[:,2]] = [0,255,0]

        for x in range(len(img_subpixel)): #for subpixel harris
            for y in range(len(img_subpixel[x])):
                # if (img_subpixel[x][y] == np.array([0, 0, 255])).all():
                #     simple_corner_coords.append((x,y))
                if (img_subpixel[x][y] == np.array([0, 255, 0])).all():
                    refined_corner_coords.append((x,y))
        
        print('Saving corner coordinates in path: '+str(mat_file_path))
        with open(mat_file_path, 'w') as file:
            for x in refined_corner_coords:
                writer = csv_write(file)
                writer.writerow(x) 
        
        return img_subpixel, refined_corner_coords 
        

def save(img, list):
    cv.imwrite('corner_detection_' + str(args["algo"]) + '_' + str(start_time) + '.png',img) 
    with open(mat_file_path, 'w') as file:
        for x in list:
            writer = csv_write(file)
            writer.writerow(x) 
    return 0

def main():
    img = img_set()
    print('3' + str(img.shape))
    marked_img, coords_list = corner_detect(img)
    save(marked_img, coords_list)

    elapsed_time = datetime.datetime.now() - start_time
    print('elapsed time: ' + str(elapsed_time))

    while True:
        cv.imshow('marked corner', marked_img) 

        if cv.waitKey(1) == ord('q'):
            break
    cv.destroyAllWindows()   

# cv.imwrite('SIMPLE_HARRIS_TEST.png',img_subpixel) 

# cv.imshow('sub pixel',img_subpixel) 


# # print('Saving corner coordinates in file: '+str(data_file))
# # with open(data_file, 'w') as file:
# #     for x in harris_corner_list:
# #         writer = csv_write(file)
# #         writer.writerow(x) 

# #sub pixel
# ret, dst_subpixel = cv.threshold(dst,0.01*dst.max(),255,0)
# dst_subpixel = np.uint8(dst_subpixel)

# # find centroids
# ret, labels, stats, centroids = cv.connectedComponentsWithStats(dst_subpixel)

# # define the criteria to stop and refine the corners
# criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.001)
# corners = cv.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)

# # Now draw them
# res = np.hstack((centroids,corners))
# res = np.int0(res)
# img_subpixel = cv.imread(filename)
# img_subpixel[res[:,1],res[:,0]]=[0,0,255]
# img_subpixel[res[:,3],res[:,2]] = [0,255,0]

# for x in range(len(img_subpixel)): #for subpixel harris
#     for y in range(len(img_subpixel[x])):
#         # if (img_subpixel[x][y] == np.array([0, 0, 255])).all():
#         #     simple_corner_coords.append((x,y))
#         if (img_subpixel[x][y] == np.array([0, 255, 0])).all():
#             refined_corner_coords.append((x,y))

# cv.imwrite('SIMPLE_HARRIS_TEST.png',img_subpixel) 

# cv.imshow('sub pixel',img_subpixel) 


if __name__ == "__main__":
    main()

# print(img_set()) 
