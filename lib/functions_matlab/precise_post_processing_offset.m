function dataset_params = precise_post_processing_offset(dataset_params, flag_debug)

offset = dataset_params.offset_in_seconds;
offset_scaled = abs(offset-max(offset(:)));
offset_median = median(offset_scaled,2);

offset_matrix = offset_median-offset_median';
frame_rate = dataset_params.frame_rate;

Fs = dataset_params.Fs;

% Determine video set closest to the median
temp = sum(abs(dataset_params.offset_in_seconds-median(dataset_params.offset_in_seconds,2)));
idx_col = find(temp == min(temp));

delta_all=zeros(1,100);
max_cor_all = zeros(1,100);
frac_all = zeros(1,100);
cnt_conv_all = zeros(1,100);

if flag_debug==1
    f = figure;
end

cnt = 1;

t_max_shift = 0.5;
j = idx_col;
t_interval = 20;

for i1 = 1:dataset_params.number_of_cameras
    for i2 = 1:dataset_params.number_of_cameras
        cnt_conv = 1;
        delta_shift = 0;
        shift_old = 0;
        shift_val_max = 0;
        while cnt_conv<5 || shift_val_max/Fs>1/frame_rate
            if i1~=i2
                t_max = max(offset_matrix(:));
                                
                t = rand(1)*(dataset_params.videoLength-t_max*2.1-t_interval);
                t_int = [t t+t_interval];
                
                [y1, ~] = audioread(dataset_params.names_videos{i1, j}, round([t_max*Fs + t_int(1)*Fs, t_max*Fs + t_int(2)*Fs]));
                [y2, ~] = audioread(dataset_params.names_videos{i2, j}, round([t_max*Fs - offset_matrix(i1, i2)*Fs + t_int(1)*Fs, t_max*Fs - offset_matrix(i1, i2)*Fs + t_int(2)*Fs]));
                
                a = randi([1, 2]);
                
                [c,lags] = xcorr(y1(:,a), y2(:,a));
                shift_val_max = max(lags(c==max(c)));
                
                delta = shift_val_max/Fs;
                
                if abs(delta)<t_max_shift
                    frac = abs(max(c)/median(c));
                    max_cor = max(c);
                    
                    offset_matrix(i1, i2) = offset_matrix(i1, i2) + delta;
                    offset_matrix(i2, i1) = offset_matrix(i2, i1) - delta;
                    
                    delta_all(cnt) = delta;
                    max_cor_all(cnt) = max_cor;
                    frac_all(cnt) = frac;
                    cnt_conv_all(cnt) = cnt_conv;
                    delta_shift = abs(shift_old-delta);
                    shift_old = delta;

                    if flag_debug==1
                        clf(f)
                        subplot(2,1,1)
                        plot(delta_all)
                        title(['Current correlation pair: ' num2str(i1),'-' num2str(i2)])
                        yline(1/frame_rate)
                        yline(-1/frame_rate)
                        ylim([-1 1])
                        xlabel('Iteration')
                        ylabel('Time shift (s)')

                        subplot(2,1,2)
                        plot(delta_all)
                        yline(1/frame_rate)
                        yline(-1/frame_rate)
                        ylim([-5/frame_rate 5/frame_rate])
                        xlabel('Iteration')
                        ylabel('Time shift (s)')
    
                        drawnow
                    end
                cnt = cnt+1;
                end
            end
            cnt_conv = cnt_conv + 1;
        end
    end
end

offset_out = offset_matrix(:, end);

dataset_params.offset_shift_post_proc_in_frames = round((offset_out-offset_median)/(1/dataset_params.frame_rate));
dataset_params.offset_matrix = offset_matrix;

dataset_params.offset_initial = median(dataset_params.offset_in_seconds, 2); 

dataset_params.offset_corrected = dataset_params.offset_matrix(1,:)';

dataset_params.offset_initial = abs(dataset_params.offset_initial - max(dataset_params.offset_initial));
dataset_params.offset_corrected = abs(dataset_params.offset_corrected - max(dataset_params.offset_corrected));

dataset_params.offset_shift_post_proc_in_frames = ...
    round((dataset_params.offset_initial - dataset_params.offset_corrected)*dataset_params.frame_rate);

% Isolate superdiagonal
superdiag = zeros(dataset_params.number_of_cameras-1, 1);

for j = 1:dataset_params.number_of_cameras-1
    superdiag(j) = dataset_params.offset_matrix(j, j+1);
end

offset_consecutive_cameras = dataset_params.offset_matrix(1,2:end)' - cumsum(superdiag);
offset_consecutive_cameras = round(offset_consecutive_cameras*dataset_params.frame_rate);

even_nums = mod(1:dataset_params.number_of_cameras-1,2)==0;
odd_nums = mod(1:dataset_params.number_of_cameras-1,2)==1;

dataset_params.offset_neighbouring_cameras = offset_consecutive_cameras(odd_nums);
dataset_params.offset_set_cameras = offset_consecutive_cameras(even_nums);

save_dir = strrep(dataset_params.input_dir,'\','_');
save_dir = strrep(save_dir,':','');

save(['results\' save_dir], 'dataset_params')
end
