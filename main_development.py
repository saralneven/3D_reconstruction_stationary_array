import os.path
from lib import SyncVideoSet
import time
import pickle

t0 = time.time()

deployment = SyncVideoSet('/Volumes/Disk_B/Predator/26_11_2022/6', recut_videos=True)

deployment.detect_calibration_videos()

deployment.get_time_lag(method='custom', number_of_videos_to_evaluate=4)

deployment.save()
print(time.time()-t0)


'''
idx_sheet = -1

# Read relevant columns from excel file
ex_file = pd.ExcelFile(input_excel)
current_sheet_name = ex_file.sheet_names[idx_sheet]
current_sheet = pd.read_excel(input_excel, current_sheet_name, usecols=[1, 2, 3, 4, 8])

# Define paths
paths_to_videos = []
data = current_sheet.T.iat

for idx in range(len(current_sheet.index)):
    if data[3, idx] == 'Deployed':
        paths_to_videos.append(os.path.join(HD_name, data[4, idx], data[0, idx], str(data[1, idx]), 'Card_'+data[2, idx]))

base_codes = []
files = os.listdir(paths_to_videos[1])

for name in files:
    if '.mp4' or '.MP4' in name:
        base_codes.append(name[4:8])

values, counts = np.unique(base_codes, return_counts=True)
base_code = values[counts > 5]

'''