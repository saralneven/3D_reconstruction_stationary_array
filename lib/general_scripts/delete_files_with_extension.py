import os

extension = '.LRV'  # extension type to remove
root = '/Volumes/2022_copy/bommie/'  # all files in this folder and its sub-folders will be analysed
delete_files = False  # if true files will be actually removed

for path, subdirs, files in os.walk(root):
    for name in files:
        if extension in name:
            print('REMOVE: ', path + '/' + name)
            if delete_files:
                print('delete')
                os.remove(path + '/' + name)
