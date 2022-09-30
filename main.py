
from lib import FishDetection
from lib import SyncVideoSet

# Path to deployment folder
input_path = '/Volumes/2022_copy/bommie/12_07_22/1'

# Create a synchronization object containing the deployment's properties
deployment = SyncVideoSet(input_path, recut_videos=False)

# Set video codec settings (https://trac.ffmpeg.org/wiki/Encode/H.264)
deployment.codec_preset = 'ultrafast'

# Determine time lag between videos
deployment.get_time_lag(method='custom', number_of_videos_to_evaluate=4)

# Get calibration videos
deployment.get_calibration_videos()

# Determine 3D camera matrices
# deployment.compute_3d_matrices()

# Run Jack detector on dataset
all_intervals = [None] * deployment.number_of_videos[0]
camera = 2

import numpy as np
interval_fish = np.concatenate(np.array([[(450)], [(470)]]), axis=0).reshape(2, 1)


for k in range(deployment.number_of_videos[0]):
    all_intervals[k] = np.concatenate([[float(370)], [float(390)]], axis=0).reshape(2, 1)
    all_intervals[k].astype(float)


j = 3
fish_detection = FishDetection(input_path + '/' + deployment.camera_names[camera] + '/' + deployment.video_names[camera][j])
fish_detection.trimmed_clips_output_path = 'results/Jack_clips/'
fish_detection.get_video_pairs_for_detected_interval(all_intervals, deployment, camera, j)


'''for j in range(1, 2): #range(deployment.number_of_videos[0]):
    fish_detection = FishDetection(input_path + '/' + deployment.camera_names[camera] + '/' + deployment.video_names[camera][j])

    fish_detection.path_to_weights = 'yolo_weights/Jack_detect2.pt'
    fish_detection.image_size_detection = '1280'
    fish_detection.confidence = '0.8'
    fish_detection.save_images = True
    fish_detection.time_interval_between_frames = 0.75  # in sec
    fish_detection.number_of_label_classes = 1
    fish_detection.trimmed_clips_output_path = 'results/Jack_clips/'

    fish_detection.extract_frames_from_video()

    fish_detection.run_detector()

    all_intervals[j] = fish_detection.get_time_intervals_for_fish(0)

    fish_detection.get_video_pairs_for_detected_interval(all_intervals, deployment, camera, j)
'''
