import subprocess
import json
import os
import sys
from scipy.io import wavfile
import time
import numpy as np
from scipy.signal import fftconvolve
from lib import ImageProcessingFunctions as ip



class SyncVideoSet:
    def __init__(self, path_in, path_out='', recut_videos=False, single_video_mode=False):
        print('---------- INITIALIZE SYNCHRONIZATION ----------')
        print('Start synchronizing video set found in', path_in)

        self.recut_videos = recut_videos
        self.path_in = path_in
        self.path_out = path_out

        self.single_video_mode = single_video_mode

        # Get the camera and video names from the sub-folders
        print('Read video folders...')
        if os.path.isdir(path_in):
            camera_names = np.sort(os.listdir(path_in))
            video_names = [None] * len(camera_names)

            for idx in range(len(camera_names)):
                video_names[idx] = np.sort(os.listdir(path_in + '/' + camera_names[idx]))

            self.flag_folder_input = True
        else:
            camera_names = []
            video_names = []
            print('ERROR: Folder does not exist')
            self.flag_folder_input = False

        self.camera_names = camera_names
        self.number_of_cameras = int(len(camera_names))
        self.number_of_videos = [None] * self.number_of_cameras
        self.base_code = [None] * self.number_of_cameras
        self.calibration_video_names = [None] * self.number_of_cameras
        self.video_names = video_names

        # Get base-code from the second, full video and remove all videos not containing this code
        print('Clean folders...')
        get_video_base_code(self)

        remove_cut_files = False
        if recut_videos:
            remove_cut_files = True

        remove_additional_videos(self, remove_cut_files)

        # Get meta deta from videos
        print('Get metadata...')
        self.fps = [None] * self.number_of_cameras
        self.sample_rate_audio = [None] * self.number_of_cameras
        self.duration = [None] * self.number_of_cameras
        self.width = [None] * self.number_of_cameras
        self.height = [None] * self.number_of_cameras
        self.audio_channels = []
        load_meta_data(self)

        # Verify input data
        print('Verify input data...')
        self.flag_same_inputs = []
        self.lag_matrix = []
        verify_input_data(self)

        # After verification of the input data we can reduce list values to single values
        self.duration = self.duration[0]
        self.fps = self.fps[0]
        self.height = self.height[0]
        self.width = self.width[0]

        # Additional empty arrays
        self.lag_out_cal = []
        self.lag_out = []

        # Coded information
        self.codec_preset = 'ultrafast'

        # 3D reconstruction preset
        self.path_to_matlab = '/Applications/MATLAB_R2022a.app/bin/matlab'

    def get_time_lag(self, method='maximum', number_of_videos_to_evaluate=4):
        print('---------- FIND TIME LAG BETWEEN VIDEOS ----------')

        folder_names = self.path_in.split('/')
        output_file_lag_matrix = 'results/lag_matrices/' + folder_names[-3] + '_' + folder_names[-2] + '_' + \
                                 folder_names[-1] + '.npy'

        if os.path.exists(output_file_lag_matrix) and not self.recut_videos:
            self.lag_matrix = np.load(output_file_lag_matrix)
            print('Video set is already analysed and this data is loaded from', output_file_lag_matrix)
        else:
            get_time_lag_matrix(self, method, number_of_videos_to_evaluate)

            with open(output_file_lag_matrix, 'wb'):
                np.save(output_file_lag_matrix, self.lag_matrix)

        # Determine final lag values
        lag_out, lag_out_cal = get_lag_vector_from_matrix(self)
        lag_out = lag_out / self.fps
        lag_out_cal = lag_out_cal / self.fps

        self.lag_out_cal = lag_out_cal
        self.lag_out = lag_out

    def cut_and_merge_videos(self, merge=False):
        print('---------- CUT AND MERGE VIDEO CHAPTERS ----------')

        if self.recut_videos:
            get_trimmed_videos(self, False)
        if merge:
            merge_synced_videos(self)

        clean_video_names(self)

    def get_calibration_videos(self):
        if self.recut_videos:
            get_trimmed_videos(self, True)
        print('start')
        clean_video_names(self)

    def compute_3d_matrices(self):
        compute_3d_matrices_matlab(self)


def get_video_base_code(self):
    if self.single_video_mode:
        find_base_code = "GH01"
    else:
        find_base_code = "GH02"

    for i in range(self.number_of_cameras):
        base_code_video = [s for s in self.video_names[i] if (find_base_code in s and ".MP4" in s and "._G" not in s)]

        if not base_code_video:
            base_code_video = [s for s in self.video_names[i] if
                               (find_base_code.replace('H', 'X') in s and ".MP4" in s and "._G" not in s)]

        self.base_code[i] = base_code_video[0][4:8]

    return self


def remove_additional_videos(params, remove_cut_files):
    for i in range(params.number_of_cameras):
        if remove_cut_files:
            files_to_delete = [s for s in params.video_names[i][:] if (params.base_code[i] not in s
                                                                       or not (".MP4" in s or ".mp4" in s)
                                                                       or "._GH" in s
                                                                       or "._GX" in s
                                                                       or "_cut" in s)]
        else:
            files_to_delete = [s for s in params.video_names[i][:] if (params.base_code[i] not in s
                                                                       or not (".MP4" in s or ".mp4" in s)
                                                                       or "._GH" in s
                                                                       or "._GX" in s)]

        for file_name in files_to_delete:

            if os.path.exists(params.path_in + str('/') + params.camera_names[i] + str('/') + file_name):
                print('REMOVED: ', params.path_in + str('/') + params.camera_names[i] + str('/') + file_name)
                os.remove(params.path_in + str('/') + params.camera_names[i] + str('/') + file_name)

    if os.path.isdir(params.path_in):
        camera_names = np.sort(os.listdir(params.path_in))

        # Replace name list with new names
        for idx in range(len(camera_names)):
            params.video_names[idx] = np.sort(os.listdir(params.path_in + '/' + camera_names[idx]))

    params.number_of_videos = [len(name) for name in params.video_names]

    return params


def load_meta_data(self):
    for idx in range(self.number_of_cameras):
        video_file = self.path_in + str('/') + self.camera_names[idx] + str('/') + self.video_names[idx][0]

        temp_file = os.path.splitext(video_file)[0] + '.json'

        subprocess.run(
            'ffprobe -v quiet -print_format json -show_format -show_streams {} > {}'.format(video_file, temp_file),
            shell=True)

        metadata = json.load(open(temp_file, 'r'))
        os.remove(temp_file)

        fps = np.array(metadata['streams'][0]['r_frame_rate'].split('/')).astype(int)
        self.audio_channels = int(metadata['streams'][1]['channels'])
        self.fps[idx] = fps[0] / fps[1]
        self.sample_rate_audio = int(metadata['streams'][1]['sample_rate'])
        self.duration[idx] = float((metadata['streams'][1]['duration']))
        self.width[idx] = (metadata['streams'][0]['width'])
        self.height[idx] = (metadata['streams'][0]['height'])


def verify_input_data(self):
    flag_fps = len(np.unique(self.fps)) == 1
    flag_resolution = len(np.unique(self.width)) == 1

    self.flag_same_inputs = flag_fps and flag_resolution

    if self.flag_same_inputs:
        print('All ' + str(self.number_of_cameras) + ' cameras have the following settings: ')
        print('Fps: ' + str(np.round(self.fps[0])))
        print('Resolution: ' + str(self.width[0]) + ' X ' + str(self.height[0]))
    else:
        print('The ' + str(self.number_of_cameras) + ' cameras do not have the same settings')
        print('Fps: ' + str(np.round(self.fps)))
        print('Resolution: ' + str(self.width) + ' X ' + str(self.height))

    if np.min(self.number_of_videos) < 1:
        print('One of the cameras has ', str(np.min(self.number_of_videos)), 'video(s). At least 2 are needed. Verify '
                                                                             'if the correct folder is addressed')
        self.flag_folder_input = False


def extract_audio(self, itr_camera, itr_video):
    video_file = self.path_in + str('/') + self.camera_names[itr_camera] + str('/') + \
                 self.video_names[itr_camera][itr_video]

    print('Audio extracted from', video_file)

    temp_file = os.path.splitext(video_file)[0] + '.wav'

    subprocess.run('ffmpeg -y -v quiet -i {} -vn -c:a pcm_s16le -ss {} -t {} {}'.format(video_file,
                                                                                        0,
                                                                                        self.duration,
                                                                                        temp_file),
                   shell=True)
    sample_rate, signal = wavfile.read(temp_file)
    os.remove(temp_file)

    return signal.mean(axis=1)


def get_shifted_matrix(mat):
    sx, sy = mat.shape
    out = np.zeros((sx, sy))

    for i in range(sx):
        out[i, :] = mat[i, :] + mat[0, i]

    return out


def get_lag_vector_from_matrix(params):
    lag_matrix_frames = np.round(params.lag_matrix * params.fps)

    rows = np.where(np.arange(len(lag_matrix_frames[:, 0])) % params.number_of_cameras == 1)
    rows = np.tile(rows, 1).transpose()

    lag_out = np.zeros(params.number_of_cameras)

    if not params.single_video_mode:
        for i in range(1, params.number_of_cameras):
            print(i)
            if i % 2 == 1:
                print(lag_matrix_frames)
                print(rows)
                values, counts = np.unique(
                    np.concatenate([lag_matrix_frames[:, i], np.squeeze(lag_matrix_frames[rows, i])]),
                    return_counts=True)
            else:
                values, counts = np.unique(lag_matrix_frames[:, i], return_counts=True)
            lag_out[i] = values[np.argmax(counts)]
    else:
        lag_out = lag_matrix_frames[0, :]

    lag_out_all = lag_out - np.min(lag_out)

    lag_out_calibration = np.zeros(params.number_of_cameras)

    for i in range(int(params.number_of_cameras / 2)):
        lag_out_calibration[i * 2:(i + 1) * 2] = lag_out[i * 2:(i + 1) * 2] - min(lag_out[i * 2:(i + 1) * 2])
    return lag_out_all, lag_out_calibration


def get_trimmed_videos(params, only_calibration):
    ts = time.time()
    for i in range(params.number_of_cameras):
        path_in = params.path_in + '/' + params.camera_names[i] + '/' + params.video_names[i][0]

        path_out = params.path_in + '/' + params.camera_names[i] + '/' + os.path.splitext(params.video_names[i][0])[
            0] + '_cut.mp4'
        path_out_cal = params.path_in + '/' + params.camera_names[i] + '/' + os.path.splitext(params.video_names[i][0])[
            0] + '_cut_cal.mp4'

        if not only_calibration:
            print(np.round(time.time() - ts, 2), 's >> Cutting video', path_out, '...')
            ip.trim_video(path_in, path_out, params.lag_out[i], params.duration)

        print(np.round(time.time() - ts, 2), 's >> Cutting video', path_out_cal, '...')
        ip.trim_video(path_in, path_out_cal, params.lag_out_cal[i], params.duration)


def merge_synced_videos(params):
    ts = time.time()
    for idx_camera_num in range(params.number_of_cameras):

        print(np.round(time.time() - ts, 2), 's >> Merging videos for: ',
              params.path_in + '/' + params.camera_names[idx_camera_num])

        # make merge list
        folder_path = params.path_in + '/' + params.camera_names[idx_camera_num]

        filenames = np.sort(os.listdir(folder_path))

        cut_found = False

        with open(folder_path + '/merge_list.txt', 'w') as f:
            for line in filenames:
                if '01' + params.base_code[idx_camera_num] in line:
                    cut_found = True
                    if '_cut' in line and '_cal' not in line:
                        f.write('file \'' + folder_path + '/' + line + '\'')
                        f.write('\n')
                elif params.base_code[idx_camera_num] in line:
                    f.write('file \'' + folder_path + '/' + line + '\'')
                    f.write('\n')

        if not cut_found:
            print('No video name containing _cut found')
            sys.exit()

        if os.path.exists(params.path_out + '/Camera_' + params.camera_names[idx_camera_num] + '.mp4'):
            os.remove(params.path_out + '/Camera_' + params.camera_names[idx_camera_num] + '.mp4')

        if not os.path.exists(params.path_out):
            os.makedirs(params.path_out)

        ip.merge_videos(params.path_out + '/Camera_' + params.camera_names[idx_camera_num] + '.mp4', folder_path +
                        '/merge_list.txt')


def get_time_lag_matrix(params, method, number_of_videos_to_evaluate):
    ts = time.time()

    if method == 'maximum':
        itr_max = int(np.min(params.number_of_videos) - 1)
    elif method == 'custom':
        itr_max = min(number_of_videos_to_evaluate, np.min(params.number_of_videos) - 1)
    else:
        print('ERROR: no correct method is assigned. Use either ''maximum'' or ''custom''')
        sys.exit()

    if params.single_video_mode:
        itr_max = 1

    out = np.zeros((params.number_of_cameras * itr_max, params.number_of_cameras))

    for itr_video in range(itr_max):
        print(np.round(time.time() - ts, 2), 's >> Analysing audio of video ', itr_video * params.number_of_cameras + 0
              + 1, '/', itr_max * params.number_of_cameras)

        res_audio = extract_audio(params, 0, itr_video)
        y = np.zeros((len(res_audio), params.number_of_cameras))
        y[:len(res_audio), 0] = res_audio

        if params.number_of_cameras > 2:
            for i in range(1, params.number_of_cameras):
                print(np.round(time.time() - ts, 2), 's >> Analysing audio of video ',
                      itr_video * params.number_of_cameras + i + 1, '/', itr_max * params.number_of_cameras)

                res_audio = extract_audio(params, i, itr_video)
                y[:len(res_audio), i] = res_audio
        else:
            i = 1
            print(np.round(time.time() - ts, 2), 's >> Analysing audio of video ',
                  itr_video * params.number_of_cameras + i + 1, '/', itr_max * params.number_of_cameras)

            res_audio = extract_audio(params, i, itr_video)
            y[:len(res_audio), i] = res_audio

        lag = np.zeros((params.number_of_cameras, params.number_of_cameras))

        for k in range(params.number_of_cameras):
            for m in range(params.number_of_cameras):
                corr = fftconvolve(y[:, k], y[::-1, m], mode='full')
                offset = np.argmax(corr)
                lag[k, m] = ((2 * y[:, k].size - 1) // 2 - offset) / int(params.sample_rate_audio)

        out[itr_video * params.number_of_cameras:(itr_video + 1) * params.number_of_cameras, :] = get_shifted_matrix(
            lag)

        params.lag_matrix = out


def clean_video_names(params):

    for idx in range(params.number_of_cameras):
        params.video_names[idx] = np.sort(os.listdir(params.path_in + '/' + params.camera_names[idx]))

    for i in range(params.number_of_cameras):
        temp = params.video_names[i][:]
        j = 0
        while j < len(temp):
            if 'cut_cal' in temp[j]:
                params.calibration_video_names[i] = temp[j]
            if 'cut' in temp[j]:
                temp = np.delete(temp, j)
                j -= 1
            j += 1
        params.video_names[i] = np.sort(temp)
        params.number_of_videos[i] = j
    return params


def compute_3d_matrices_matlab(params):
    for set_number in range(params.number_of_cameras // 2):
        name1 = params.path_in + '/' + params.camera_names[set_number * 2] + '/' + \
                params.calibration_video_names[set_number * 2]
        name2 = params.path_in + '/' + params.camera_names[set_number * 2 + 1] + '/' + \
                params.calibration_video_names[set_number * 2 + 1]

        folder_names = params.path_in.split('/')
        save_folder = 'results/calib_results/' + folder_names[-3] + '_' + folder_names[-2] + '_' + folder_names[-1] + \
                      '_' + params.camera_names[set_number * 2] + params.camera_names[set_number * 2 + 1]

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        os.system(
            params.path_to_matlab + ' -nodesktop -nosplash -r "python_run_matlab_camera_calibration(\'' + name1 +
            '\',\'' + name2 + '\',\'' + save_folder + '\')"')
