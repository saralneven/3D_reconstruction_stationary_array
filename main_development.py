import os
from lib import SyncVideoSet
from lib import FishDetection
import numpy as np
import scipy as sp

fish_type = 0
all_predator = np.load('results/names_all_deployments_predator.npy', allow_pickle=True)

for i in range(6, 19):
    input_path = all_predator[i]
    deployment = SyncVideoSet(input_path, '', remove_cut_files=True)

    for j in range(1, deployment.number_of_videos[0]):
        print(deployment.video_names[0][j])
        detect_jack = FishDetection(input_path + '/' + deployment.camera_names[0] + '/' + deployment.video_names[0][j])

        detect_jack.time_interval_between_frames = 1

        detect_jack.number_of_images = len(os.listdir('images/detection_images/' + detect_jack.base_name + '/.'))

        results = np.zeros((detect_jack.number_of_label_classes, detect_jack.number_of_images))

        path_to_labels = detect_jack.path_to_results + '/labels'
        deployment.number_of_images_with_detection = len(os.listdir(path_to_labels))
        s = os.listdir(path_to_labels)

        for k in range(deployment.number_of_images_with_detection-1):
            with open(path_to_labels + '/' + s[k]) as f:
                lines = f.readlines()

            for l in range(len(lines)):
                results[int(lines[l][0]), int(float(s[k][9:17]) / 1000 / detect_jack.time_interval_between_frames-1)] += 1

        kernel_size = 7
        fish_present = sp.signal.convolve(results[fish_type, :], np.ones(kernel_size), mode='same') / kernel_size > 0.7

        fish_enters = np.where(np.diff(fish_present * 1) == 1)
        t1 = (fish_enters[fish_type]) * detect_jack.time_interval_between_frames
        fish_leaves = np.where(np.diff(fish_present * 1) == -1)
        t2 = (fish_leaves[fish_type]) * detect_jack.time_interval_between_frames

        interval_fish = np.concatenate([t1, t2], axis=0).reshape(2, len(t1))

        # post-processing to trim and merge videos
        interval_fish = np.round(interval_fish)

        interval_fish[0, :] = interval_fish[0, :] - 6
        interval_fish[1, :] = interval_fish[1, :] + 6

        # if clips are closer than 10 sec, merge clips
        c = 0
        s = len(interval_fish[0, :]) - 1

        while c < s:
            if (interval_fish[0, c + 1] - interval_fish[1, c]) < 20:
                interval_fish[1, c] = interval_fish[1, c + 1]
                interval_fish = np.delete(interval_fish, c + 1, axis=1)
                s = len(interval_fish[0, :]) - 1
            else:
                c += 1
        detect_jack.trimmed_clips_output_path = 'results/Jack_clips/'
        detect_jack.store_video_clips_for_detected_interval(interval_fish)