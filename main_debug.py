import cv2
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import os, shutil
from lib import ImageProcessingFunctions as ip

frames_per_x_sec = 1

name1 = '/Volumes/2022_copy/Test_calib/1/A/GH010004_cut_cal.mp4'
name2 = '/Volumes/2022_copy/Test_calib/1/B/GH010003_cut_cal.mp4'

folder = 'images/calib_images'

for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

ip.extract_frames(name1, frames_per_x_sec, folder=folder)
ip.extract_frames(name2, frames_per_x_sec, folder=folder)

img1_path = 'images/calib_images/GH010003_cut_cal/GH010003_cut_cal_0000100.jpg'
img2_path = 'images/calib_images/GH010004_cut_cal/GH010004_cut_cal_0000100.jpg'

