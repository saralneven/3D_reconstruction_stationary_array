
from lib import FishDetection
from lib import SyncVideoSet
import numpy as np
import time

ts = time.time()

all_predator = np.load('results/names_all_deployments_bommie.npy', allow_pickle=True)

for i in range(1, len(all_predator)): #len(all_predator)):
    try:
        ts = time.time()
        input_path = all_predator[i]
        deployment = SyncVideoSet(input_path, '', remove_cut_files=True)

        for j in range(1, deployment.number_of_videos[0]):
            print(deployment.video_names[0][j])
            fish_detection = FishDetection(input_path + '/' + deployment.camera_names[0] + '/' + deployment.video_names[0][j])

            fish_detection.path_to_weights = 'yolo_weights/Jack_detect2.pt'
            fish_detection.image_size_detection = '1280'
            fish_detection.confidence = '0.8'
            fish_detection.save_images = True
            fish_detection.time_interval_between_frames = 0.75  # in sec
            fish_detection.number_of_label_classes = 1
            fish_detection.trimmed_clips_output_path = 'results/Jack_clips/'

            fish_detection.extract_frames_from_video()
            fish_detection.run_detector()

            try:
                intervals = fish_detection.get_time_intervals_for_fish(0)
                fish_detection.store_video_clips_for_detected_interval(intervals)
            except Exception:
                pass
            print(time.time()-ts)
    except Exception:
        pass


'''fish_detection = FishDetection('/Volumes/Synced/predator/15_07_22/2/Camera_J.MP4')

fish_detection.path_to_weights = 'yolo_weights/jack_detector.pt'
fish_detection.image_size_detection = '1440'
fish_detection.confidence = '0.6'
fish_detection.save_images = True
fish_detection.time_interval_between_frames = 1  # in sec
fish_detection.number_of_label_classes = 1
fish_detection.trimmed_clips_output_path = '/Volumes/Synced/Jack_clips/'


fish_detection.extract_frames_from_video()
fish_detection.run_detector()
fish_detection.get_time_intervals_for_fish(0)
print(ts)

fish_detection.store_video_clips_for_detected_interval(5)

'''