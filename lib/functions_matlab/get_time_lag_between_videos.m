
function dataset_params = get_time_lag_between_videos(dataset_params, idx_sync_videos)
    s = length(idx_sync_videos);
    offset = zeros(dataset_params.number_of_cameras, s);

    for k = 1:s
        disp(['Reading audio tracks (' num2str(k) '/' num2str(s) ')...'])
        disp(['File ' num2str(1) '\' num2str(dataset_params.number_of_cameras)])
        
        [temp, Fs] = audioread(dataset_params.names_videos{1, idx_sync_videos(k)});
        dataset_params.videoLength = length((temp(:,1)))/Fs;
        
        y1 = zeros(length(temp(:, 1)), dataset_params.number_of_cameras);
        y1(1:length(temp(:, 1)), 1) = temp(:, 1);
        %y2 = zeros(length(temp(:, 1)), dataset_params.number_of_cameras);
        
        parfor i = 2:dataset_params.number_of_cameras
            disp(['File ' num2str(i) '\' num2str(dataset_params.number_of_cameras)])
            [temp, ~] = audioread(dataset_params.names_videos{i, idx_sync_videos(k)});
        
            y1(1, i) = temp(:, 1);
            %y2(:, i) = temp(:, 2);
        end
        
        disp(['Correlating audio files (' num2str(k) '/' num2str(s) ')...'])
        parfor i = 1:dataset_params.number_of_cameras-1
            disp(['File ' num2str(i) '\' num2str(dataset_params.number_of_cameras-1)])
            [c,lags] = xcorr(y1(:, 1), y1(:, i+1));
            offset(i+1, k) = max(lags(c==max(c)));
        end 
        
        % shift such that the first video starts with an offset of 0
        if min(offset(:, k))<0
            offset(:, k) = offset(:, k)+abs(min(offset(:, k)));
        end
    end

    dataset_params.offset_in_seconds = offset/Fs;
    dataset_params.Fs = Fs;

    save_dir = strrep(dataset_params.input_dir,'\','_');
    save_dir = strrep(save_dir,':','');

    save(['results\' save_dir], 'dataset_params')
end