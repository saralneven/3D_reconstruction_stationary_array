import os
import numpy as np

path = '/Volumes/2022_copy/predator'
dirs_path = os.listdir(path)
subdir_max = 20

all_dirs = None

for name in dirs_path:
    for i in range(subdir_max):
        if os.path.exists(path + '/' + name + '/' + str(i)):
            all_dirs = np.append(all_dirs, path + '/' + name + '/' + str(i))

with open('../../../3D_reconstruction/results/names_all_deployments_predator.npy', 'wb') as f:
    np.save('../../../3D_reconstruction/results/names_all_deployments_predator.npy', all_dirs)

