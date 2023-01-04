from lib import FishDetection
from lib import SyncVideoSet
from lib import ImageProcessingFunctions as ip

# Path to deployment folder
input_path = '/Volumes/2022_copy/predator/19_07_22/2'

# Create a synchronization object containing the deployment's properties
deployment = SyncVideoSet(input_path, recut_videos=True, single_video_mode=True, calibration_video_mode=0)

# Determine time lag between videos
deployment.get_time_lag()

# Get calibration videos
deployment.get_calibration_videos()

