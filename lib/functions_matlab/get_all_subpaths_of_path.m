rootdir = 'D:\predator';

subdir = dir(rootdir);

video_dir_all = cell(length(subdir)*2-4, 1);
c=1;
num_of_subdir=2;

for i  = 3:length(subdir)
    for j =1:num_of_subdir
        temp = [subdir(i).folder '\' subdir(i).name '\' num2str(j)];

        if exist(temp)
            video_dir_all{c} = temp;
            c=c+1;
        end
    end
end

video_dir_all = video_dir_all(1:c-1);

save('results\predator_files','video_dir_all')