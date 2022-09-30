function write_synced_videos_2_output(dataset_params, video_dir_out)

offset = dataset_params.offset_corrected;

for i = 1:dataset_params.number_of_cameras
    tic
    disp(['Camera ' num2str(i)])
    video_name = dataset_params.names_videos{i,1};
    video_dir = dataset_params.input_dir;
    
    s_start = seconds(offset(i,:));
    s_end = seconds(dataset_params.duration);
    
    s_start.Format = 'hh:mm:ss.SSS';
    s_end.Format = 'hh:mm:ss.SSS';
    
    path_input = [video_dir '\' dataset_params.names_camera{i,1} '\' dataset_params.names_videos{i,1}];
    path_output = insertBefore(path_input,".MP4","_cut");
    
    if exist(path_output)==2
        delete((path_output))
    end

    if exist([video_dir '\' dataset_params.names_camera{i,1} '\' 'output.mp4'])==2
        delete([video_dir '\' dataset_params.names_camera{i,1} '\' 'output.mp4'])
    end

    ffmpeg_cut_command = ['ffmpeg -ss ' char(s_start) ' -i ' path_input ' -t ' char(s_end) ' -c copy ' path_output];
    
    disp(['Writing to path: ' video_dir '\' dataset_params.names_camera{i,1}])
    
    txt = cell(dataset_params.number_of_cameras, 1);
    txt{1, 1} = ['file ' '''' path_output ''''];
    
    for j = 2:dataset_params.number_of_cameras
        if ~isempty(dataset_params.names_videos{i,j})
            txt{j, 1} = ['file ' '''' video_dir '\' dataset_params.names_camera{i,1} '\' dataset_params.names_videos{i,j} ''''];
        end
    end 
    
    writecell(txt, [video_dir '\' dataset_params.names_camera{i,1} '\Merge_list.txt'])

    if ~exist([video_dir_out '\Synced'])
        mkdir([video_dir_out '\Synced'])
    end
    
    ffmpeg_merge_command = ['ffmpeg -safe 0 -f concat -i ' video_dir '\' dataset_params.names_camera{i,1} '\' 'Merge_list.txt' ' -c copy ' video_dir_out '\Synced\Camera_' dataset_params.names_camera{i,1} '.mp4'];
    
    disp('Cut first video...')
    system(ffmpeg_cut_command);
    toc
    disp('Merge videos...')
    system(ffmpeg_merge_command);
    toc
end