from lib import FishDetection
import numpy as np
import os

path_in1 = 'results/Jack_clips/17_07_22_2_A_GH020745_1_cam1.MP4'
path_in2 = 'results/Jack_clips/17_07_22_2_B_GH020745_1_cam2.MP4'

for path in [path_in1, path_in2]:
    fish_detection = FishDetection(path)

    fish_detection.path_to_weights = 'yolo_weights/Jack_detect2.pt'
    fish_detection.image_size_detection = '1280'
    fish_detection.confidence = '0.8'
    fish_detection.save_images = False
    fish_detection.time_interval_between_frames = 1/60  # in sec
    fish_detection.number_of_label_classes = 1
    fish_detection.trimmed_clips_output_path = 'results/Jack_clips/'

    fish_detection.extract_frames_from_video()
    fish_detection.run_detector()

fish_detection.number_of_images = len(os.listdir('images/detection_images/' + fish_detection.base_name + '/.'))-1
path_to_labels = fish_detection.path_to_results + '/labels'

fish_detection.number_of_images_with_detection = len(os.listdir(path_to_labels))
s = np.sort(os.listdir(path_to_labels))

t = np.zeros(fish_detection.number_of_images)

for i in range(fish_detection.number_of_images_with_detection):
    temp = path_to_labels + '/' + s[i]
    t[i] = float(temp[-12:-4])/1000
    with open(path_to_labels + '/' + s[i]) as f:
        lines = f.readlines()

