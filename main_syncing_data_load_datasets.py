from lib import *

input_path = '/Volumes/2022_copy/bommie/11_07_22/1'
output_path = '/Volumes/Synced/bommie/11_07_22/1'

deployment = SyncVideoSet(input_path, output_path)


# deployment.lag_matrix = np.load('results/lag_matrices/11_07_22_1.npy')

folder_names = input_path.split('/')
output_file_lag_matrix = 'results/lag_matrices/' + folder_names[-2] + '_' + folder_names[-1] + '.npy'
# np.save('results/' + path_save + '.npy', res)

#deployment.get_time_lag()