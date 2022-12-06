import numpy as np
import cv2 as cv
from pathlib import Path
from csv import writer as csv_write
import sys
import datetime

#initialisation stuff
time_now = datetime.datetime.now()
np.set_printoptions(threshold=sys.maxsize)
harris_corner_list = []
harris_mask_list = []
subpixel_harris_corner_list_A = []
subpixel_harris_corner_list_B = []
filename = 'calib_square_v11.png'
# filename = 'real_image_fine.png'


#declare save locations
data_folder = Path(__file__).parent / 'harris'
img_folder = data_folder / 'images'
data_filename_img = 'testharris_img_' + str(time_now) + '.csv'
data_file = data_folder / data_filename_img 

data_filename_mat = 'testharris_mat_' + str(time_now) + '.csv'
data_file2 = data_folder / data_filename_mat

data_filename_img2 = 'testharris_img2_' + str(time_now) + '.csv'
data_file3 = data_folder / data_filename_img2

data_filename_corners = 'corner_coords_' + str(time_now) + '.csv'
data_file4 = data_folder / data_filename_corners

data_filename_mask = 'mask_coords' + str(time_now) + '.csv'
data_file5 = data_folder / data_filename_mask

data_filename_subpixel = 'subpixel_coords_' + str(time_now) + '.csv'
data_file6 = data_folder / data_filename_subpixel

with open(data_file4, 'w') as file:
    writer = csv_write(file)
    writer.writerow(["coordinates", "average coordinates"])    
with open(data_file6, 'w') as file:
    writer = csv_write(file)
    writer.writerow(["A coordinates", "B coordinates", "average coordinates"]) 

harris_img = 'harris_' + str(time_now) + '.jpg'
harris_img_dilated = 'harris_dilated_' + str(time_now) + '.jpg'
harris_file = img_folder / harris_img
harris_dilated_file = img_folder / harris_img_dilated

harris_subpixel_img = 'harris_subpixel_' + str(time_now) + '.jpg'
harris_subpixel_img_dilated = 'harris_subpixel_dilated' + str(time_now) + '.jpg'
harris_subpixel_file = img_folder / harris_subpixel_img
harris_subpixel_dilated_file = img_folder / harris_subpixel_img_dilated

#harris corner detection
img = cv.imread(filename)
gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
ret,gray = cv.threshold(gray,127,255,cv.THRESH_BINARY)
gray = np.float32(gray)
dst = cv.cornerHarris(gray,2,3,0.04)


# Threshold for an optimal value, it may vary depending on the image.
mat = dst>0.01*dst.max()
img[mat] = np.array([0, 0, 255])


#dilated for marking the corners, for visualisation purposes not important
img_dilated = img
dst_dilated = cv.dilate(dst,None)
mat_dilated = dst_dilated>0.01*dst_dilated.max()
img_dilated[mat_dilated] = np.array([0, 0, 255])


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
img_subpixel = cv.imread(filename)
img_subpixel[res[:,1],res[:,0]]=[0,0,255]
img_subpixel[res[:,3],res[:,2]] = [0,255,0]

# #DILATED
# #sub pixel, dilated
# ret, dst_subpixel_dilated = cv.threshold(dst_dilated,0.01*dst_dilated.max(),255,0)
# dst_subpixel_dilated = np.uint8(dst_subpixel_dilated)

# # find centroids, dilated
# ret, labels_dilated, stats_dilated, centroids_dilated = cv.connectedComponentsWithStats(dst_subpixel_dilated)

# # define the criteria to stop and refine the corners, dilated
# corners_dilated = cv.cornerSubPix(gray,np.float32(centroids_dilated),(5,5),(-1,-1),criteria)

# # Now draw them dilated
# res_dilated = np.hstack((centroids_dilated,corners_dilated))
# res_dilated = np.int0(res_dilated)
# img_subpixel_dilated = cv.imread(filename)
# img_subpixel_dilated[res_dilated[:,1],res_dilated[:,0]]=[0,0,255]
# img_subpixel_dilated[res_dilated[:,3],res_dilated[:,2]] = [0,255,0]


#check and output all pixels that are corners
for x in range(len(img)): #for normal harris
    for y in range(len(img[x])):
        if (img[x][y] == np.array([0, 0, 255])).all():
            harris_corner_list.append((x,y))

for x in range(len(mat)): #for normal harris' mask 
    for y in range(len(mat[x])):
        if (mat[x][y] == True):
            harris_mask_list.append((x,y))

for x in range(len(img_subpixel)): #for subpixel harris
    for y in range(len(img_subpixel[x])):
        if (img_subpixel[x][y] == np.array([0, 0, 255])).all():
            subpixel_harris_corner_list_A.append((x,y))
        elif (img_subpixel[x][y] == np.array([0, 255, 0])).all():
            subpixel_harris_corner_list_B.append((x,y))


# saving all relevant files as data
print('Saving 1st coordinates in file: '+str(data_file))
with open(data_file, 'a') as file:
    for x in img:
        writer = csv_write(file)
        writer.writerow(x) 
print('Saving mat coordinates in file: '+str(data_file2))
with open(data_file2, 'a') as file:
    for x in mat:
        writer = csv_write(file)
        writer.writerow(x) 
print('Saving 2nd coordinates in file: '+str(data_file3))
with open(data_file3, 'a') as file:
    for x in img:
        writer = csv_write(file)
        writer.writerow(x) 
print('Saving corner coordinates in file: '+str(data_file4))
with open(data_file4, 'a') as file:
    for x in harris_corner_list:
        writer = csv_write(file)
        writer.writerow(x) 
print('Saving mask coordinates in file: '+str(data_file5))
with open(data_file5, 'a') as file:
    for x in harris_mask_list:
        writer = csv_write(file)
        writer.writerow(x) 
print('Saving subpixel corner coordinates in file: '+str(data_file6))
with open(data_file6, 'a') as file:
    for x in range(len(max(subpixel_harris_corner_list_A, subpixel_harris_corner_list_B))):
        writer = csv_write(file)
        writer.writerow([subpixel_harris_corner_list_A[x],subpixel_harris_corner_list_B[x]]) 
    

#saving images
cv.imwrite(str(harris_file),img) #harris, non dilated
# cv.imwrite(str(harris_dilated_file),img_dilated) #harris, non dilated
cv.imwrite(str(harris_subpixel_file),img_subpixel) #harris subpixel, non dilated
# cv.imwrite(str(harris_subpixel_dilated_file),img_subpixel_dilated) #harris subpixel, non dilated


#show images
cv.imshow('dst',img) #harris, non dilated
# cv.imshow('dst dilated',img_dilated) #harris, dilated
cv.imshow('sub pixel',img_subpixel) #harris subpixel, non dilated
# cv.imshow('sub pixel dilated',img_subpixel_dilated) #harris subpixel, dilated


#show time elapsed
time_elapsed = datetime.datetime.now() - time_now
print('time elapsed: ' + str(time_elapsed))

if cv.waitKey(0) & 0xff == 27:
    cv.destroyAllWindows()
