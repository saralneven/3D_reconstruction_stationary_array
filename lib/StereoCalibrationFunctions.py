import cv2 as cv


def index_images(image_names, t_interval, delta_t):
    images = []
    c_time = 0

    for image_name in image_names:
        if t_interval[1] >= c_time >= t_interval[0]:
            im = cv.imread(image_name, 1)
            images.append(im)
        c_time += delta_t

    return images