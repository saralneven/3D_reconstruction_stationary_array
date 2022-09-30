## To do
- What happens when we exceed 99 chapters (13h) in the file naming of gopro? May have an effect on the merge script. 
will we ever make videos that long?
- Performance of yolo7
- Write more comments in the script
-----------------------------------------------------
## Timing

The computation time seems to be dominated by the transfer and creation speed of the video data.
the full videos of 1h are about 30gb each, which adds up to 180gb of video data that needs to be read, cut and stored 
again. The table below shows the timing results of bommie dataset 12/07/22/1

Note there is a lot depending on the compression method.

| Task                                                          | execution time (1h) | execution time (8h) |
|:--------------------------------------------------------------|--------------------:|--------------------:|
| Offloading 6 memory cards                                     |               - min |               - min |
| Syncing for 6 cameras and 4 video chapters per camera: 15 min |              15 min |              15 min |
| Cutting videos 6 videos                                       |              36 min |              13 min |
| Merging videos 6 videos                                       |             124 min |             432 min |
| Compute 3D matrices for 3 camera pairs                        |               - min |               - min |
| Total:                                                        |               - min |               - min |

-----------------------------------------------------
## Synchronizing videos
The **SyncVideoSet** class found in the **lib** folder can be used to synchronize a set of videos. The **__init__** 
function was specifically written to analyse video sets obtained from GoPro video cameras. This part can be re-written 
to make the scripts usable for other camera types. All the other steps are independent of the cameras used.



### Description of the computational steps
1. The main folder is given as an input. The script analyses the subfolders and determines all the names of the videos
produced by the gopro. 
2. Once all the names of the videos are determined, the video files are read and the audio files are isolated.
3. For N cameras, and NxN matrix is computed with the relative lag between the cameras. Position M(c1, c2) gives the 
time lag between camera c1 and c2. These values are obtained by correlating the time signals and computing the maximum of 
value. 
4. As each row l gives the time lag between camera l and the others, we add each M[1, l] to row M[l, :] such that each 
row corresponds to the same time lag between cameras.
5. As the gopro generates individual 4GB video  files, the process is repeated for a user-defined number of additional 
videos. Taking more videos will improve the accuracy of the algorithm.
6. This above results in a (N*number of video sets)xN matrix where each row gives the time lag between camera 1 and the 
other N-1 cameras. Here we filter for outliers and give the estimated lag between neighbouring cameras a higher weight as 
they have the closed spatial distance and will typically have a small time-difference between the first and second camera 
turning on.
7. The found time lag is then used to cut all video such that each frame matches in time
8. We define the **_cut** and **_cut_cal** videos as the presentation of the checkerboard is sometimes done before all
cameras have been turned on. The cut_cal only takes neighbouring cameras into account whereas the cut file takes all 
cameras into account.

### FFMPEG and decoding
After evaluating more videos I found that some of them were not cut on a frame accurate. 

on encoding: https://trac.ffmpeg.org/wiki/Encode/H.264#FAQ 

[h264 @ 0x7f8a9d020580] No start code is found.
[h264 @ 0x7f8a9d020580] Error splitting the input into NAL units.
Error while decoding stream #0:0: Invalid data found when processing input

#### Lag matrix
The lag matrix obtained in step 6 is shown in the figure below. We can see that in each column, the correlation operation 
comes to slightly different values in most cases. We then compute the corresponding number frames for each time value as 
a way to round these values. The most frequent frame shift number is than chosen for cutting the videos in step 7. 

![lag matrix](images/offset_matrix.png)

#### Compression
The use of data compression with the h.264 codec reduces the sice of the videos by a factor of 3 to 6.
However, it is highly variable 

- Noted that the largest videos correspond to the tripod cameras. More movement?
- avg 47gb per bommie per hour per 6 cameras. That's about 400gb per 8 hours per 6 cameras 
- larger for 17/07/11
- 
- ![lag matrix](images/Size_difference.png)

-----------------------------------------------------
## 3D calibration
For now, we are just addressing the Matlab code due to the checkerboard detection algorithm error.

-----------------------------------------------------
## YOLOv5 installation

#### Error log
I got the error "urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:997)>
" while running the dataset = project.version(1).download("yolov5")

Solved it through **pip install --upgrade certifi** 