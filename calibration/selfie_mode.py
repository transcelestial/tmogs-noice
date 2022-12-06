import cv2 as cv
import datetime
import argparse
from csv import writer as csv_write
from pathlib import Path
from math import trunc

start_time = datetime.datetime.now()

# scale_percent = 100 # percent of original size
# width = int(1440 * scale_percent / 100)
# height = int(1080 * scale_percent / 100)
# dim = (width, height)

#declare save locations
data_folder = Path(__file__).parent / 'calibration_images_3'

try:
    camera1 = cv.VideoCapture("/dev/video" + str(1), cv.CAP_V4L2)
    camera1.set(cv.CAP_PROP_FOURCC,
    cv.VideoWriter_fourcc('Y', '1', '0', ' '))
    camera1.set(cv.CAP_PROP_CONVERT_RGB, 0)
    camera1.set(cv.CAP_PROP_FPS, 60)
    if not camera1.isOpened():
        print("Cannot open camera")

    n_frames = 0
    tick = 2
    n_pix = 0
    while True:
        ret1, frame1 = camera1.read()
        frame1 = cv.convertScaleAbs(frame1, alpha=0.25)

        # frame1 = cv.resize(frame1, dim, interpolation = cv.INTER_AREA)

        cv.imshow('coarse camera', frame1)
        if (trunc((datetime.datetime.now() - start_time).total_seconds()) == tick):
            print('saving image ' + str(n_pix) + '...')
            destination = str(data_folder) + '/' + str(n_pix) + '.png'
            cv.imwrite(destination, frame1)
            tick += 2
            n_pix += 1

        if cv.waitKey(1) == ord('q'):
            break

        n_frames += 1

except KeyboardInterrupt:
    print('Interrupted')
            
print("FPS: ", n_frames/(datetime.datetime.now() - start_time).total_seconds())

camera1.release()
cv.destroyAllWindows()