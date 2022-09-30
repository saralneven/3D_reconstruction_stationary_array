function [cam_images] = extract_paired_images(video_paths,calib_frames)
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here

for i = 1:length(video_paths)
    v = VideoReader(video_paths{i});
    newfolder = sprintf("images/calib_images/%d",i);
    mkdir(newfolder)
    cd(newfolder)


    for i = calib_frames
        frame = read(v,[i i]);
        filename = sprintf('im_%06d.jpg', i);
        imwrite(frame,filename,'jpg')
    end

    cd('../../..')
end

DirList = dir(fullfile("images/calib_images/1", '*.jpg'));
cam1_images = fullfile("images/calib_images/1", {DirList.name});
DirList = dir(fullfile("images/calib_images/2", '*.jpg'));
cam2_images = fullfile("images/calib_images/2", {DirList.name});
cam_images=[cam1_images;cam2_images];