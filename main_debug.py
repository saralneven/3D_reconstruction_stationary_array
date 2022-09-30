
'''import numpy as np
np.load('results/names_all_deployments_bommie.npy')'''

import os

name1 = '/Volumes/2022_copy/predator/14_07_22/3/H/GH017477_cut_cal.mp4'
name2 = '/Volumes/2022_copy/predator/14_07_22/3/I/GH016449_cut_cal.mp4'

save_folder = 'results/calib_results/predator_14_07_22_3_HI'

if not os.path.exists(save_folder):
    os.makedirs(save_folder)

os.system('/Applications/MATLAB_R2022a.app/bin/matlab -nodesktop -nosplash -r "python_run_matlab_camera_calibration(\''
          + name1 + '\',\'' + name2 + '\',\'' + save_folder + '\')"')