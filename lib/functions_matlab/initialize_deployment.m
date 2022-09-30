% Input: directory to folder containing the gopro videos for all cameras
% used in the deployment
%
% Ouput: returns a structure containing the sorted names of the videos that
% need to be synced

function dataset_params = initialize_deployment(video_dir)
    tic

	disp('Initializing data from folder...')
    camera_names = dir(video_dir);

    dataset_params.input_dir = video_dir;

    for i = 1:length(camera_names)
        if contains(camera_names(i).name,'Synced')
            camera_names(i) = [];  
        end
    end
    
    % Determin the total number of cameras
    dataset_params.number_of_cameras = length(camera_names)-2;
    
    % Empty cell structure for storing file names
    dataset_params.names_videos = cell(dataset_params.number_of_cameras,1);
    dataset_params.names_camera = cell(dataset_params.number_of_cameras,1);
    
    % Loop over subfolders to extract names of all files
    for i = 1:dataset_params.number_of_cameras
        dataset_params.names_camera{i, 1} =  camera_names(2+i).name;
        temp_dir = dir([video_dir '/' camera_names(2+i).name]);
    
        addpath([video_dir '/' camera_names(2+i).name])
    
        c=1;
    
        for j = 1:length(temp_dir)-2
             temp = temp_dir(2+j).name;
    
             % Only store files with a mp4 format
             if contains(temp , 'MP4') && ~contains(temp , '._') && ~contains(temp , '_cut')
                dataset_params.names_videos{i, c} = temp;
                c = c+1;
             end
        end
    end

    % Remove unwanted videos
    dataset_params.base_code = cell(dataset_params.number_of_cameras, 1);
    [~, dataset_params.number_of_videos] = size(dataset_params.names_videos);
    
    % find video sequence code by identifying the last part of the name of the
    % second video. Here we assume that if we have a full deployement, we have
    % at least 2 full videos made by the gopro (8 min /16 min video)
    
    for i = 1:dataset_params.number_of_cameras
        for j=1:dataset_params.number_of_videos 
            if strfind(dataset_params.names_videos{i, j},'GH02')
                base_code = extractAfter(dataset_params.names_videos{i, j},'GH02');
                base_code = extractBefore(base_code,'.MP4');
                dataset_params.base_code{i, 1} = base_code;
            end
        end
    end
    
    % Use the sequence codes to remove other videos which are not part of the
    % sequence
    for i = 1:dataset_params.number_of_cameras
        for j = 1:dataset_params.number_of_videos 
            if ~any(strfind(dataset_params.names_videos{i, j}, dataset_params.base_code{i, 1}))
                dataset_params.names_videos{i, j} = 'ZZZ';
            end
            if isempty(dataset_params.names_videos{i, j})
                dataset_params.names_videos{i, j} = 'ZZZ';
            end
        end
    end
    
    % sort the sequence names
    for i = 1:dataset_params.number_of_cameras
        dataset_params.names_videos(i,:) = sort(dataset_params.names_videos(i,:));
    end
    
    % remove unnecessary cells
    for i = 1:dataset_params.number_of_cameras
        for j=1:dataset_params.number_of_videos 
            if any(strfind(dataset_params.names_videos{i, j},'ZZZ'))
                dataset_params.names_videos{i, j} = [];
            end
        end
    end
    
    empt_mat = zeros(size(dataset_params.names_videos));
    
    for i = 1:dataset_params.number_of_cameras
        for j=1:dataset_params.number_of_videos 
            empt_mat(i,j) = isempty(dataset_params.names_videos{i,j});
        end
    end
    
    dataset_params.names_videos(:, sum(empt_mat) == dataset_params.number_of_cameras) = [];
    dataset_params.number_of_videos = length(dataset_params.names_videos(1,:));
    dataset_params.number_videos_all_cameras = dataset_params.number_of_videos...
        - nnz(sum(cellfun(@isempty,dataset_params.names_videos)));

    
    % prepare empty structure elements for storing data in next step
    dataset_params.video_length_in_frames = dataset_params.names_videos;
    dataset_params.videoReader_objects = dataset_params.names_videos;
    dataset_params.video_size = dataset_params.names_videos;

    % get video settings
    v = VideoReader(dataset_params.names_videos{1,1});

    dataset_params.imagesize=[v.Height,v.Width];
    dataset_params.frame_rate = v.FrameRate; 
    dataset_params.duration_of_video = v.Duration;

    disp([num2str(dataset_params.number_of_cameras) ' cameras found'])
end