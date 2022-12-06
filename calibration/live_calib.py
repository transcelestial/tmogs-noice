import numpy as np
import cv2 as cv
from pathlib import Path
from csv import writer as csv_write
import sys
import datetime
import argparse

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(
    description='First var: output. 0 for fine cam, 1 for coarse cam, 2 for preset picture. Default is 2./n\
        Second var: bool to show frames. Default is False.')

ap.add_argument("output", nargs='?', default=2, type=int,
                help="0 for fine, 1 for coarse, 2 for preset pic")
ap.add_argument("boolframe", nargs='?', default=False, type=bool,
                help="bool to show frames")

args = vars(ap.parse_args())

start_time = datetime.datetime.now()
simple_corner_coords = []
refined_corner_coords = []

scale_percent = 50 # percent of original size
width = int(1440 * scale_percent / 100)
height = int(1080 * scale_percent / 100)
dim = (width, height)

#declare save locations
data_folder = Path(__file__).parent / 'harris'
img_folder = data_folder / 'images'
mat_file = 'mat_corners.csv'
mat_file_path = data_folder / mat_file 

with open(mat_file_path, 'w') as file:
    writer = csv_write(file)
    #writer.writerow(['CAM0_COORDS', 'CAM1_COORDS', 'TRANSLATION', 'ROTATION'])

def img_set():
    if args["img"] == 2:
        #using predefined image
        filename = 'calib_square_v11_rot_10.png'
        img = cv.imread(filename)
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
            cv.imshow('Press any key to freeze frame', frame)
            if cv.waitKey(1) == ord('q'):
                img = frame
                break
    
        return img
        
    if args["img"] == 1:
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
            cv.imshow('Press any key to freeze frame', frame)
            if cv.waitKey(1) == ord('q'):
                break
        
        img = frame
        return img

def zoom_at(img, zoom=1, angle=0, coord=None):
    
    cy, cx = [ i/2 for i in img.shape[:-1] ] if coord is None else coord[::-1]
    
    rot_mat = cv.getRotationMatrix2D((cx,cy), angle, zoom)
    result = cv.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv.INTER_LINEAR)

    return result

def cropping(gray):
    # resize image
    # gray = cv.resize(gray, dim, interpolation = cv.INTER_AREA)
    frame8 = cv.convertScaleAbs(gray, alpha=0.25)
    return frame8

def log(x):
    with open(mat_file_path, 'w') as file:
        writer = csv_write(file)
        writer.writerow([x]) 

def coord_ave(list):
    pass

def corner_detect(img):
    print('now calculating checkerboard...')
    retval, corners = cv.findChessboardCorners(img, (9, 8), None)
    print('finalising checkerboard...')
    if (retval) == False:
        fnl = img
    else:
        fnl = cv.drawChessboardCorners(img, (9, 8), corners, retval)
    log(corners) 
    print('now displaying checkerboard...')
    while True:
        cv.imshow('frozen', fnl)
        if cv.waitKey(1) == ord('q'):
            break     

def main():
    if args["output"] == 2:
        print('Starting demo tracking')
        #using predefined image
        filename = 'calib_square_v11_rot_10.png'
        img = cv.imread(filename)
            
        #     camera0 = cv.VideoCapture("/dev/video" + str(0), cv.CAP_V4L2)
        #     camera0.set(cv.CAP_PROP_FOURCC,
        #             cv.VideoWriter_fourcc('Y', '1', '0', ' '))
        #     camera0.set(cv.CAP_PROP_CONVERT_RGB, 0)
        #     camera0.set(cv.CAP_PROP_FPS, 60)
        #     if not camera0.isOpened():
        #         print("Cannot open camera")
        #         return
            
        #     camera1 = cv.VideoCapture("/dev/video" + str(1), cv.CAP_V4L2)
        #     camera1.set(cv.CAP_PROP_FOURCC,
        #             cv.VideoWriter_fourcc('Y', '1', '0', ' '))
        #     camera1.set(cv.CAP_PROP_CONVERT_RGB, 0)
        #     camera1.set(cv.CAP_PROP_FPS, 60)
        #     if not camera1.isOpened():
        #         print("Cannot open camera")
        #         return
                
        #     n_frames = 0

        #     while True:
        #         ret0, frame0 = camera0.read()  # Capture frame-by-frame
        #         ret1, frame1 = camera1.read()
        #         # if frame is read correctly ret is True
        #         if not ret0:
        #             print("Can't receive frame (stream end?) from cam0. Exiting ...")
        #             break
        #         if not ret1:
        #             print("Can't receive frame (stream end?) from cam1. Exiting ...")
        #             break

        #         lined_frame0 = cropping(frame0)
        #         lined_frame1 = cropping(frame1)

        #         #retval0, corners0 = cv.findChessboardCorners(lined_frame0, (6, 4), None)
        #         retval1, corners1 = cv.findChessboardCorners(lined_frame1, (7, 4), None)

        #         # if(retval0) == False:
        #         #     fnl0 = lined_frame0
        #         # else:
        #         #     fnl0 = cv.drawChessboardCorners(lined_frame0, (6, 4), corners0, retval0)

        #         if (retval1) == False:
        #             fnl1 = lined_frame1
        #         else:
        #             fnl1 = cv.drawChessboardCorners(lined_frame1, (7, 4), corners1, retval1)

        #         if args["boolframe"]:
        #             cv.imshow('gray0', lined_frame0)
        #             # cv.imshow('gray1', lined_frame1)
        #             # cv.imshow("corners0", fnl0)
        #             cv.imshow("corners1", fnl1)
                
        #         if n_frames == 0:
        #             cv.moveWindow("gray0", 20,40)
        #             cv.moveWindow("gray1", 20,640)

        #         if cv.waitKey(1) == ord('q'):
        #             break

        #         n_frames += 1

        # except KeyboardInterrupt:
        #     print('Interrupted')

        # print("FPS: ", n_frames/(datetime.datetime.now() - start).total_seconds())

        # camera0.release()
        # camera1.release()
        # cv.destroyAllWindows()
    
    elif args["output"] == 1:
        try:
            print('Starting demo tracking')

            camera = cv.VideoCapture("/dev/video0", cv.CAP_V4L2)
            camera.set(cv.CAP_PROP_FOURCC,
                    cv.VideoWriter_fourcc('Y', '1', '0', ' '))
            camera.set(cv.CAP_PROP_CONVERT_RGB, 0)
            camera.set(cv.CAP_PROP_FPS, 60)
            if not camera.isOpened():
                print("Cannot open camera")
                return

            n_frames = 0
            while True:
                ret, frame = camera.read()  # Capture frame-by-frame
                # if frame is read correctly ret is True
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break
                frame = cropping(frame)
                cv.imshow('Press any key to freeze frame', frame)
                if cv.waitKey(1) == ord('q'):
                    img = frame
                    break     
                n_frames += 1         
            
            
        except KeyboardInterrupt:
            print('Interrupted')

        camera.release()
        cv.destroyAllWindows()





    elif args["output"] == 0:
        try:
            print('Starting demo tracking')

            camera = cv.VideoCapture("/dev/video0", cv.CAP_V4L2)
            camera.set(cv.CAP_PROP_FOURCC,
                    cv.VideoWriter_fourcc('Y', '1', '0', ' '))
            camera.set(cv.CAP_PROP_CONVERT_RGB, 0)
            camera.set(cv.CAP_PROP_FPS, 60)
            if not camera.isOpened():
                print("Cannot open camera")
                return
            
            n_frames = 0
            while True:
                ret, frame = camera.read()  # Capture frame-by-frame
                # if frame is read correctly ret is True
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break
            
                lined_frame = cropping(frame)

                retval, corners = cv.findChessboardCorners(lined_frame, (9, 8), None)
                if (retval) == False:
                    fnl = lined_frame
                else:
                    fnl = cv.drawChessboardCorners(lined_frame, (9, 8), corners, retval)

                if args["boolframe"]:
                    cv.imshow("corners", fnl)      

                if cv.waitKey(1) == ord('q'):
                    break

                n_frames += 1

        except KeyboardInterrupt:
            print('Interrupted')

        camera.release()
        cv.destroyAllWindows()

    corner_detect(img)



if __name__ == "__main__":
    main()

