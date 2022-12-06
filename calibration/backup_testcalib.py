import cv2 as cv
import datetime
import argparse
from csv import writer as csv_write
from pathlib import Path

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(
    description='First var: bool to show frames. Default is False./n\
        Second var: int for x position of actual center, default is 720/n\
        Third var: int for y position of actual center, default is 540')

ap.add_argument("output", nargs='?', default=1, type=int,
                help="0 for fine, 1 for coarse")
ap.add_argument("boolframe", nargs='?', default=True, type=bool,
                help="bool to show frames")
ap.add_argument("w", nargs='?', default=720, type=int,
                help="int x pos of defined center")
ap.add_argument("h", nargs='?', default=540, type=int,
                help="int y pos of defined center")

args = vars(ap.parse_args())

# determined center
actual_center = (args["w"], args["h"])

data_folder = Path(__file__).parent / 'data'
data_suffix = '.csv'
data_filename = 'csvdata'
data_file = data_folder / data_filename 
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
        writer.writerow(['T_ELAPSED', 'X_ERROR', 'Y_ERROR'])

start = datetime.datetime.now()

def compute_dist(frame, actual_center, final):
    x_error = final[0] - actual_center[0]  # print it out
    y_error = final[1] - actual_center[1]
    str_x = str(round(x_error, 2))
    str_y = str(round(y_error, 2))
    cv.line(frame, (int(final[0]), int(final[1])),
            actual_center, (255, 255, 255), 1)
    print('X_error= ' + str_x)
    print('Y_error= ' + str_y)
    time_elapsed = datetime.datetime.now() - start
    with open(data_file, 'a') as file:
        writer = csv_write(file)
        writer.writerow([time_elapsed, x_error, y_error]) 

    cv.putText(
        img=frame,
        text="actual center:" +
        str(round(actual_center[0], 2)) + ", " +
        str(round(actual_center[1], 2)),
        org=(100, 50),
        fontFace=cv.FONT_HERSHEY_DUPLEX,
        fontScale=1.0,
        color=(255, 255, 255),
        thickness=1
    )
    cv.putText(
        img=frame,
        text="beacon center: " +
        str(round(final[0], 2)) + ", " + str(round(final[1], 2)),
        org=(100, 100),
        fontFace=cv.FONT_HERSHEY_DUPLEX,
        fontScale=1.0,
        color=(255, 255, 255),
        thickness=1
    )
    cv.putText(
        img=frame,
        text="x_error: " + str_x + "    y_error: " + str_y,
        org=(100, 150),
        fontFace=cv.FONT_HERSHEY_DUPLEX,
        fontScale=1.0,
        color=(255, 255, 255),
        thickness=1
    )
    return frame


def cropping(gray):
    # print("reso", gray.shape)
    height_gray = gray.shape[0]
    width_gray = gray.shape[1]
    padding = 25
    (minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(gray)
    # print("maxLoc", maxLoc)
    # print("maxVal", maxVal)
    width_start = min(max(maxLoc[0]-padding, 0), width_gray)
    width_end = min(max(maxLoc[0] + padding, 0), width_gray)
    height_start = min(max(maxLoc[1]-padding, 0), height_gray)
    height_end = min(max(maxLoc[1]+padding, 0), height_gray)
    # print("bounding box", height_start, height_end, width_start, width_end)

    frame8 = cv.convertScaleAbs(gray, alpha=0.25)
    # crop_frame8 = frame8[height_start:height_end,
    #                      width_start:width_end]  # height, width
    # cv.imshow('crop 8', crop_frame8)

    crop_frame = gray[height_start:height_end,
                      width_start:width_end]  # height, width
    ret, thresh1 = cv.threshold(crop_frame, 127, 255, cv.THRESH_TOZERO)
    # calculate moments of THRESH image
    M = cv.moments(thresh1)
    # calculate x,y coordinate of center
    if M["m00"] != 0:
        cX = (M["m10"] / M["m00"])
        cY = (M["m01"] / M["m00"])
    else:
        cX, cY = 0, 0
        return

    # print("center coord", cX, cY)

    final_coord = (width_start+cX, height_start+cY)

    print("final coord", final_coord)

    lined_frame = compute_dist(frame8, actual_center, final_coord)

    cv.circle(lined_frame, (int(width_start+cX),
                            int(height_start+cY)), 20, 255, 1)
    tracking_frame = lined_frame
    return lined_frame

def start_demo_tracking_callback():
    try:
        print('Starting demo tracking')

        camera = cv.VideoCapture("/dev/video" + str(args["output"]), cv.CAP_V4L2)
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

            if args["boolframe"]:
                cv.imshow('gray', lined_frame)
            if cv.waitKey(1) == ord('q'):
                break

            n_frames += 1

    except KeyboardInterrupt:
        print('Interrupted')

    print("FPS: ", n_frames/(datetime.datetime.now() - start).total_seconds())

    camera.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    start_demo_tracking_callback()

