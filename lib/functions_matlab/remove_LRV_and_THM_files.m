function remove_LRV_and_THM_files(rootdir)
% Deletes all files with LRV and THM extentions contained in the root
% folder
    filelist = dir(fullfile(rootdir, '**\*.*'));  
    filelist = filelist(~[filelist.isdir]);  
    
    for i = 1:length(filelist)
        if contains(filelist(i).name,'.LRV') || contains(filelist(i).name,'.THM')
            delete([filelist(i).folder '\' filelist(i).name])
        end
    end
end
