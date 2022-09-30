from lib import FishDetection
from lib import SyncVideoSet
from lib import ImageProcessingFunctions as ip

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

camera_pair = 1  # 1=[A,B] 2=[C,D] etc. Alphabetic order of the cameras is assumed throughout the scripts
video_chapter = 3
t_start = 300
t_end = 310
output_path = 'results/clips/'

# Cut clip in pairs
ip.cut_video_pairs(deployment, camera_pair, video_chapter, t_start, t_end, input_path, output_path)

