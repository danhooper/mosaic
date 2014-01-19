#!/usr/bin/python
import datetime
from multiprocessing import Pool
import os
import sys
import time
from PIL import Image

IMAGE_DIR = 'imgs/'
master_size = (7200, 10800)
indiv_size = (master_size[0]/50, master_size[1]/75)

def get_image_pix(image_file):
    img = Image.open('%s%s' % (IMAGE_DIR, image_file))
    img = img.resize(indiv_size, Image.ANTIALIAS)
    image = {
        'pixels': img.tostring(),
        'size': img.size,
        'mode': img.mode,
    }
    return (image, list(img.getdata()))

def print_map_async_status(map_result, should_sleep=True):
    while not map_result.ready():
        sys.stdout.write('%d ' % map_result._number_left)
        sys.stdout.flush()
        if should_sleep:
            time.sleep(1)
    sys.stdout.write('\n')

def get_image_list():
    image_dir_list = os.listdir('%s' % IMAGE_DIR)
    print(image_dir_list)
    img_pix_list = []
    pool = Pool()
    map_result = pool.map_async(get_image_pix, image_dir_list)
    sys.stdout.write('Images left:')
    print_map_async_status(map_result)
    results = map_result.get()
    pool.close()
    return results

def CalculateImageDiff(images):
    master_img_piece = images[0]
    image = images[1]
    diff = sum(map(CalculateDiff, master_img_piece, image[1]))
    return diff

def CalculateDiff(master, img):
    diff = abs(master[0] - img[0]) + abs(master[1] - img[1]) + abs(master[2] - img[2])
    return diff

def main2():


    im = Image.open("%ssource.jpg" % IMAGE_DIR)
    master_img = im.resize(master_size, Image.ANTIALIAS)
    print('resized source image')

    image_list = get_image_list()
    print('build list of images and their pixels')
    print (master_size[0], indiv_size[0])
    print (master_size[1], indiv_size[1])
    pool = Pool()
    for x in range(0, master_size[0], indiv_size[0]):
        for y in range(0, master_size[1], indiv_size[1]):
            master_img_piece = master_img.crop((x, y, x + indiv_size[0], y + indiv_size[1]))
            master_img_pix = list(master_img_piece.getdata())
            sys.stdout.write('Checking for best image in %d %d:' % (x, y))
            image_list_temp = [(master_img_pix, image) for image in image_list]
            img_results = pool.map(CalculateImageDiff, image_list_temp)
            unused_val, best_diff_idx = min((val, idx) for (idx, val) in
                                            enumerate(img_results))
            best_img = image_list[best_diff_idx][0]
            master_img.paste(Image.fromstring(best_img['mode'],
                                              best_img['size'],
                                              best_img['pixels']), (x, y))
    pool.close()
    master_img.save('master_image.jpg', "JPEG")


import cProfile
main2()


