import cv2 as cv
import datetime
import argparse
from csv import writer as csv_write
from pathlib import Path
import argparse
from math import trunc, atan, sqrt, pi
from time import sleep

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(
    description='...')
ap.add_argument("input", nargs='?', default=0, type=int,
                help="0 for using coarse camera, 1 for using fine camera. 2 for both cameras. Default is 0.")
ap.add_argument("mode", nargs='?', default=0, type=int,
                help="0 for just looking through camera, 1 for using selfie mode, 2 for orientation mode. Default is 0. If input == 2, raw output is given")

args = vars(ap.parse_args())

start_time = datetime.datetime.now()

CHECKERBOARD = (7,4)
checker_center_row = [0, 0]
checker_center_column = [0, 0]
checker_center = [0, 0]
frame_center = [720, 540]


#declare save locations
data_folder = Path(__file__).parent / 'calibration_images_nfov'

scale_percent =100 # percent of original size
width = int(1440 * scale_percent / 100)
height = int(1080 * scale_percent / 100)
dim = (width, height)
period = 2

if args["input"] in (0,2):
    camera0 = cv.VideoCapture("/dev/video" + str(0), cv.CAP_V4L2)
    camera0.set(cv.CAP_PROP_FOURCC,
    cv.VideoWriter_fourcc('Y', '1', '0', ' '))
    camera0.set(cv.CAP_PROP_CONVERT_RGB, 0)
    camera0.set(cv.CAP_PROP_FPS, 60)

    if not camera0.isOpened():
        print("Cannot open camera 0")

if args["input"] in (1,2):
    camera1 = cv.VideoCapture("/dev/video" + str(1), cv.CAP_V4L2)
    camera1.set(cv.CAP_PROP_FOURCC,
    cv.VideoWriter_fourcc('Y', '1', '0', ' '))
    camera1.set(cv.CAP_PROP_CONVERT_RGB, 0)
    camera1.set(cv.CAP_PROP_FPS, 60)

    if not camera1.isOpened():
        print("Cannot open camera 1")

try:
    n_frames = 0
    tick = 1
    n_pix = 0
    while True:
        if args["input"] == 0:
            ret0, frame0 = camera0.read()  # Capture frame-by-frame
            frame0 = cv.convertScaleAbs(frame0, alpha=0.25)
            frame0 = cv.resize(frame0, dim, interpolation = cv.INTER_AREA)

            if args["mode"] == 0: #normal mode
                cv.imshow('coarse camera (NORMAL MODE)', frame0)

                if cv.waitKey(1) == ord('q'):
                    break

                n_frames += 1


            elif args["mode"] == 1: #selfie mode
                while True:
                    cv.imshow('coarse camera (SELFIE MODE)', frame0)
                    if (trunc((datetime.datetime.now() - start_time).total_seconds()) == tick):
                        print('saving image ' + str(n_pix) + '...')
                        destination = str(data_folder) + '/' + str(n_pix) + '.png'
                        cv.imwrite(destination, frame0)
                        tick += period
                        n_pix += 1
                    
                    if cv.waitKey(1) == ord('q'):
                        break
                    
                    n_frames += 1

            elif args["mode"] == 2: #orientation mode
                # orientation_timer = datetime.datetime.now()
                # if (trunc((datetime.datetime.now() - orientation_timer).total_seconds()) == tick):
                ret, corners = cv.findChessboardCorners(frame0, CHECKERBOARD, cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_FAST_CHECK + cv.CALIB_CB_NORMALIZE_IMAGE)
                if ret == True:
                    x_distance_px = corners[0][0][0] - corners[CHECKERBOARD[0] - 1][0][0]
                    y_distance_px = corners[0][0][1] - corners[CHECKERBOARD[0] - 1][0][1]
                    angle_disp = ((atan(y_distance_px/x_distance_px))/(2*pi))*180

                    checker_center_row[0] = corners[0][0][0] + (corners[CHECKERBOARD[0] - 1][0][0] - corners[0][0][0])/2
                    checker_center_row[1] = corners[0][0][1] + (corners[CHECKERBOARD[0] - 1][0][1] - corners[0][0][1])/2
                    # print('1: {}'.format(center1))

                    checker_center_column[0] = corners[- CHECKERBOARD[0]][0][0] + (corners[-1][0][0] - corners[- CHECKERBOARD[0]][0][0])/2
                    checker_center_column[1] = corners[- CHECKERBOARD[0]][0][1] + (corners[-1][0][1] - corners[- CHECKERBOARD[0]][0][1])/2
                    # print('2: {}'.format(center2))

                    checker_center[0] =  checker_center_row[0] + (checker_center_column[0] - checker_center_row[0])/2
                    checker_center[1] =  checker_center_row[1] + (checker_center_column[1] - checker_center_row[1])/2
                    # print('c: {}'.format(center))

                    center_disp_x = frame_center[0] - checker_center[0]
                    center_disp_y = frame_center[1] - checker_center[1]
                    cv.drawMarker(frame0, (int(checker_center[0]), int(checker_center[1])), (255, 255, 255), cv.MARKER_CROSS, 20, 5, 8)
                    cv.drawMarker(frame0, (0, 0), (255, 255, 255), cv.MARKER_CROSS, 20, 7, 8)
                    cv.line(frame0, (int(corners[0][0][0]), int(corners[0][0][1])),
                            (int(corners[CHECKERBOARD[0] - 1][0][0]), int(corners[CHECKERBOARD[0] - 1][0][1])), (255, 255, 255), 1)
                    
                    cv.putText(
                        img=frame0,
                        text="Rotation angle (degrees): {}   X displacement: {}   Y: displacement: {}   frame number: {}".format(angle_disp, center_disp_x, center_disp_y, n_frames),
                        org=(100, 50),
                        fontFace=cv.FONT_HERSHEY_DUPLEX,
                        fontScale=1.0,
                        color=(255, 255, 255),
                        thickness=1
                    )

                cv.imshow('coarse camera (ORIENTATION MODE)', frame0)
                if cv.waitKey(1) == ord('q'):
                    break
                else:
                    cv.waitKey(2000)

                n_frames += 1
        
        if args["input"] == 1:
            ret1, frame1 = camera1.read()
            frame1 = cv.convertScaleAbs(frame1, alpha=0.25)
            frame1 = cv.resize(frame1, dim, interpolation = cv.INTER_AREA)
            cv.imshow('coarse camera', frame1)
            
            if args["mode"] == 1:
                if (trunc((datetime.datetime.now() - start_time).total_seconds()) == tick):
                    print('saving image ' + str(n_pix) + '...')
                    destination = str(data_folder) + '/' + str(n_pix) + '.png'
                    cv.imwrite(destination, frame1)
                    tick += period
                    n_pix += 1

            if cv.waitKey(1) == ord('q'):
                break


        if args["input"] == 2:
            ret0, frame0 = camera0.read()  # Capture frame-by-frame
            frame0 = cv.convertScaleAbs(frame0, alpha=0.25)
            frame0 = cv.resize(frame0, dim, interpolation = cv.INTER_AREA)

            ret1, frame1 = camera1.read()
            frame1 = cv.convertScaleAbs(frame1, alpha=0.25)
            frame1 = cv.resize(frame1, dim, interpolation = cv.INTER_AREA)
            
            cv.imshow('fine camera', frame0)
            cv.imshow('coarse camera', frame1)
            
            if cv.waitKey(1) == ord('q'):
                break      

        # if n_frames == 0:
        #     cv.moveWindow('fine camera', 20,40)
        #     cv.moveWindow('coarse camera', 20,500)
        n_frames += 1

except KeyboardInterrupt:
    print('Interrupted')
            
print("FPS: ", n_frames/(datetime.datetime.now() - start_time).total_seconds())

if args["input"] in (0,2):
    camera0.release()
if args["input"] in (1,2):
    camera1.release()
cv.destroyAllWindows()