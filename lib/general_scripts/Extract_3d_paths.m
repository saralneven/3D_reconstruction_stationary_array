% read in two images
A=imread("calib_images/1/im_008471.jpg");
B=imread("calib_images/2/im_008471.jpg");

% undistort images
A = undistortImage(A,stereoParams.CameraParameters1);
B = undistortImage(B,stereoParams.CameraParameters2);

% show images and calculate pixel coords of the cam A and B
imshow(A)
imshow(B)

% below I hard coded values I measured
lc1=[1683,530]
rc1=[1919,536]
lc2=[1645,616]
rc2=[1893,634]

%calculate 3d pos of left cam
point3d_lr = triangulate(lc1, lc2, stereoParams);

%calculate 3d pos of right cam
point3d_rc = triangulate(rc1, rc2, stereoParams);

% calc inter-camera distance (ans = 1.001 m)
sqrt(sum((point3d_lr-point3d_rc).^2))