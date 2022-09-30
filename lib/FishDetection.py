import os
import shutil
import numpy as np
import scipy as sp
from lib import ImageProcessingFunctions as ip
import copy


class FishDetection:
    def __init__(self, path):
        self.path_to_weights = []
        self.image_size_detection = '1280'
        self.confidence = '0.6'
        self.save_images = False
        self.time_interval_between_frames = 0.75  # in sec
        self.base_name = get_base_name(path)
        self.path = path
        self.path_to_results = 'results/fish_detection/' + self.base_name
        self.trimmed_clips_output_path = []

        self.duration = []
        self.number_of_images = []
        self.number_of_images_detected = 0
        self.number_of_images_with_detection = 0
        self.number_of_label_classes = 10

    def extract_frames_from_video(self):
        ip.extract_frames(self.path, self.time_interval_between_frames)

    def run_detector(self):
        run_detector(self)

    def get_time_intervals_for_fish(self, fish_type):
        return compute_interval_where_fish_x_is_present(self, fish_type)

    def store_video_clips_for_detected_interval(self, intervals):
        video_file_input = self.path
        base_name = self.base_name

        split_name = video_file_input.split('/')

        print(self.trimmed_clips_output_path)

        for idx in range(len(intervals[0, :])):
            video_file_output = self.trimmed_clips_output_path + split_name[-4] + '_' + split_name[-3] + '_' + \
                                split_name[-2] + '_' + base_name + '_' + str(idx + 1) + '.mp4'

            print('Wrinting output: ', video_file_output)
            if os.path.exists(video_file_output):
                os.remove(video_file_output)
            ip.cut_video(video_file_input, video_file_output, int(intervals[0, idx]),
                         int(intervals[1, idx]))

    def get_video_pairs_for_detected_interval(self, all_intervals, deployment, camera, video_number):
        trim_video_pairs(self, all_intervals, deployment, camera, video_number)

def get_base_name(path):
    base_name = os.path.splitext(os.path.basename(path))[0]
    return base_name


def run_detector(params):
    if os.path.exists(params.path_to_results):
        shutil.rmtree(params.path_to_results)

    if params.save_images:
        os.system("python lib/detect.py"
                  " --weights " + params.path_to_weights +
                  " --img " + params.image_size_detection +
                  " --conf " + params.confidence +
                  " --source images/detection_images/" + params.base_name +
                  " --save-txt "
                  " --project results/fish_detection "
                  " --name " + params.base_name)
    else:
        os.system("python lib/detect.py"
                  " --weights " + params.path_to_weights +
                  " --img " + params.image_size_detection +
                  " --conf " + params.confidence +
                  " --source images/detection_images/" + params.base_name +
                  " --save-txt "
                  " --nosave "
                  " --project results/fish_detection "
                  " --name " + params.base_name)


def compute_interval_where_fish_x_is_present(params, fish_type):
    params.number_of_images = len(os.listdir('images/detection_images/' + params.base_name + '/.'))

    results = np.zeros((params.number_of_label_classes, params.number_of_images))

    path_to_labels = params.path_to_results + '/labels'
    params.number_of_images_with_detection = len(os.listdir(path_to_labels))
    s = os.listdir(path_to_labels)

    for i in range(params.number_of_images_with_detection):
        with open(path_to_labels + '/' + s[i]) as f:
            lines = f.readlines()

        for j in range(len(lines)):
            results[int(lines[j][0]), int(float(s[i][9:17]) / 1000 / params.time_interval_between_frames - 1)] += 1

    kernel_size = 4
    fish_present = sp.signal.convolve(results[fish_type, :], np.ones(kernel_size), mode='same') / kernel_size > 0.7
    print(fish_present)

    fish_enters = np.where(np.diff(fish_present * 1) == 1)
    t1 = (fish_enters[fish_type]) * params.time_interval_between_frames
    fish_leaves = np.where(np.diff(fish_present * 1) == -1)
    t2 = (fish_leaves[fish_type]) * params.time_interval_between_frames

    interval_fish = np.concatenate([t1, t2], axis=0).reshape(2, len(t1))

    # post-processing to trim and merge videos
    interval_fish = np.round(interval_fish)

    interval_fish[0, :] = interval_fish[0, :] - 5
    interval_fish[1, :] = interval_fish[1, :] + 3

    # if clips are closer than 10 sec, merge clips
    c = 0
    s = len(interval_fish[0, :]) - 1

    while c < s:
        if (interval_fish[0, c + 1] - interval_fish[1, c]) < 10:
            interval_fish[1, c] = interval_fish[1, c + 1]
            interval_fish = np.delete(interval_fish, c + 1, axis=1)
            s = len(interval_fish[0, :]) - 1
        else:
            c += 1

    return interval_fish


def trim_video_pairs(params, all_intervals, deployment, camera, video_number):
    all_intervals_second_camera = copy.deepcopy(all_intervals)
    all_intervals[video_number][:, :] = all_intervals[video_number][:, :] + deployment.lag_out_cal[camera]
    all_intervals_second_camera[video_number][:, :] = all_intervals_second_camera[video_number][:, :] + deployment.lag_out_cal[
        camera + 1]
    print(all_intervals)
    print(all_intervals_second_camera)
    for idx in range(len(all_intervals[video_number][0, :])):
        path_in = deployment.path_in + '/' + deployment.camera_names[camera] + '/' + deployment.video_names[camera][
            video_number]
        split_name = path_in.split('/')
        print(split_name)
        path_out = params.trimmed_clips_output_path + split_name[-4] + '_' + split_name[-3] + '_' + \
                   split_name[-2] + '_' + params.base_name + '_' + str(idx + 1) + '_cam1.mp4'

        t1 = min(all_intervals[video_number][0, idx], deployment.duration)
        t2 = min(all_intervals[video_number][1, idx], deployment.duration)

        ip.cut_video(path_in, path_out, t1, t2)

        path_in = deployment.path_in + '/' + deployment.camera_names[camera + 1] + '/' + \
                  deployment.video_names[camera + 1][video_number]

        split_name = path_in.split('/')
        path_out = params.trimmed_clips_output_path + split_name[-4] + '_' + split_name[-3] + '_' + \
                   split_name[-2] + '_' + params.base_name + '_' + str(idx + 1) + '_cam2.mp4'

        t1 = min(all_intervals_second_camera[video_number][0, idx], deployment.duration)
        t2 = min(all_intervals_second_camera[video_number][1, idx], deployment.duration)

        ip.cut_video(path_in, path_out, t1, t2)
