import cv2 as cv
import datetime
import argparse
from csv import writer as csv_write
from pathlib import Path

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(
    description='First var: output camera. 0 for fine, 1 for coarse, 2 for both. Default is 2./n\
        Second var: bool to show frames. Default is True.')

ap.add_argument("output", nargs='?', default=2, type=int,
                help="0 for fine, 1 for coarse, 2 for both cameras")
ap.add_argument("boolframe", nargs='?', default=True, type=bool,
                help="bool to show frames")

args = vars(ap.parse_args())

start = datetime.datetime.now()

scale_percent = 50 # percent of original size
width = int(1440 * scale_percent / 100)
height = int(1080 * scale_percent / 100)
dim = (width, height)

data_folder = Path(__file__).parent / 'data'
data_suffix = '.csv'
data_filename = 'csvdata'
data_file = data_folder / data_filename 
append = 1
if data_file.exists():
    print('File name clash. Iterating...')
    append = 1
    while data_file.exists():
        data_file = data_folder / (data_filename + str(append) + data_suffix)
        append += 1
    print('Found allowable file: '+str(data_file))
else:
    data_file = data_folder / (data_filename + data_suffix)
    print('Saving in: '+str(data_file))

with open(data_file, 'w') as file:
        writer = csv_write(file)
        #writer.writerow(['CAM0_COORDS', 'CAM1_COORDS', 'TRANSLATION', 'ROTATION'])

def zoom_at(img, zoom=1, angle=0, coord=None):
    
    cy, cx = [ i/2 for i in img.shape[:-1] ] if coord is None else coord[::-1]
    
    rot_mat = cv.getRotationMatrix2D((cx,cy), angle, zoom)
    result = cv.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv.INTER_LINEAR)

    return result

def cropping(gray):
    # resize image
    resize_frame = cv.resize(gray, dim, interpolation = cv.INTER_AREA)
    frame8 = cv.convertScaleAbs(resize_frame, alpha=0.25)
    if args["output"] == 1:
        frame8 = zoom_at(frame8, 3, coord=(360,270))
    return frame8

def log(x):
    with open(data_file, 'a') as file:
        writer = csv_write(file)
        writer.writerow([x]) 

def coord_ave(list):
    pass

def corner_detection():
    if args["output"] == 2:
        try:
            print('Starting demo tracking')

            camera0 = cv.VideoCapture("/dev/video" + str(0), cv.CAP_V4L2)
            camera0.set(cv.CAP_PROP_FOURCC,
                    cv.VideoWriter_fourcc('Y', '1', '0', ' '))
            camera0.set(cv.CAP_PROP_CONVERT_RGB, 0)
            camera0.set(cv.CAP_PROP_FPS, 60)
            if not camera0.isOpened():
                print("Cannot open camera")
                return
            
            camera1 = cv.VideoCapture("/dev/video" + str(1), cv.CAP_V4L2)
            camera1.set(cv.CAP_PROP_FOURCC,
                    cv.VideoWriter_fourcc('Y', '1', '0', ' '))
            camera1.set(cv.CAP_PROP_CONVERT_RGB, 0)
            camera1.set(cv.CAP_PROP_FPS, 60)
            if not camera1.isOpened():
                print("Cannot open camera")
                return
                
            n_frames = 0

            while True:
                ret0, frame0 = camera0.read()  # Capture frame-by-frame
                ret1, frame1 = camera1.read()
                # if frame is read correctly ret is True
                if not ret0:
                    print("Can't receive frame (stream end?) from cam0. Exiting ...")
                    break
                if not ret1:
                    print("Can't receive frame (stream end?) from cam1. Exiting ...")
                    break

                lined_frame0 = cropping(frame0)
                lined_frame1 = cropping(frame1)

                #retval0, corners0 = cv.findChessboardCorners(lined_frame0, (6, 4), None)
                retval1, corners1 = cv.findChessboardCorners(lined_frame1, (7, 4), None)

                # if(retval0) == False:
                #     fnl0 = lined_frame0
                # else:
                #     fnl0 = cv.drawChessboardCorners(lined_frame0, (6, 4), corners0, retval0)

                if (retval1) == False:
                    fnl1 = lined_frame1
                else:
                    fnl1 = cv.drawChessboardCorners(lined_frame1, (7, 4), corners1, retval1)

                if args["boolframe"]:
                    cv.imshow('gray0', lined_frame0)
                    # cv.imshow('gray1', lined_frame1)
                    # cv.imshow("corners0", fnl0)
                    cv.imshow("corners1", fnl1)
                
                if n_frames == 0:
                    cv.moveWindow("gray0", 20,40)
                    cv.moveWindow("gray1", 20,640)

                if cv.waitKey(1) == ord('q'):
                    break

                n_frames += 1

        except KeyboardInterrupt:
            print('Interrupted')

        print("FPS: ", n_frames/(datetime.datetime.now() - start).total_seconds())

        camera0.release()
        camera1.release()
        cv.destroyAllWindows()
    
    elif args["output"] == 1:
        try:
            print('Starting demo tracking')

            camera = cv.VideoCapture("/dev/video1", cv.CAP_V4L2)
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

                retval, corners = cv.findChessboardCorners(lined_frame, (7, 4), None)
                if (retval) == False:
                    fnl = lined_frame
                else:
                    fnl = cv.drawChessboardCorners(lined_frame, (7, 4), corners, retval)

                log(corners)

                if args["boolframe"]:
                    cv.imshow("corners", fnl)      

                if cv.waitKey(1) == ord('q'):
                    break

                n_frames += 1

        except KeyboardInterrupt:
            print('Interrupted')

        print("FPS: ", n_frames/(datetime.datetime.now() - start).total_seconds())

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

                retval, corners = cv.findChessboardCorners(lined_frame, (7, 4), None)
                if (retval) == False:
                    fnl = lined_frame
                else:
                    fnl = cv.drawChessboardCorners(lined_frame, (7, 4), corners, retval)

                if args["boolframe"]:
                    cv.imshow("corners", fnl)      

                if cv.waitKey(1) == ord('q'):
                    break

                n_frames += 1

        except KeyboardInterrupt:
            print('Interrupted')

        print("FPS: ", n_frames/(datetime.datetime.now() - start).total_seconds())

        camera.release()
        cv.destroyAllWindows()

if __name__ == "__main__":
    corner_detection()

