#!/usr/bin/python
import datetime
from multiprocessing import Pool
import os
import sys
import time
from PIL import Image

class MosaicImage(object):

    def __init__(self, img):
        self.image_dict = {
            'pixels': img.tostring(),
            'size': img.size,
            'mode': img.mode,
        }
        self.pixel_list = list(img.getdata())

    def get_pil_image(self):
        return Image.fromstring(self.image_dict['mode'],
                                self.image_dict['size'],
                                self.image_dict['pixels'])

class Sector(object):

    def __init__(self, source_img, image_list, x, y):
        self.source_img = source_img
        self.image_list = image_list
        self.x = x
        self.y = y
        self.best_idx = None

    def get_best_image(self):
        return self.image_list[self.best_idx]

class SectorResult(object):
    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.y = y

IMAGE_DIR = 'imgs/'
master_size = (7200, 10800)
indiv_size = (master_size[0]/50, master_size[1]/75)

def get_resized_image(image_file):
    img = Image.open('%s%s' % (IMAGE_DIR, image_file))
    img = img.resize(indiv_size, Image.ANTIALIAS)
    return MosaicImage(img)

def print_map_async_status(map_result, should_sleep=True):
    while not map_result.ready():
        sys.stdout.write('%d ' % map_result._number_left)
        sys.stdout.flush()
        if should_sleep:
            time.sleep(1)
    sys.stdout.write('\n')

def get_image_list():
    image_dir_list = os.listdir('%s' % IMAGE_DIR)
    pool = Pool()
    for img in image_dir_list:
        get_resized_image(img)
    map_result = pool.map_async(get_resized_image, image_dir_list)
    sys.stdout.write('Images left:')
    print_map_async_status(map_result)
    results = map_result.get()
    pool.close()
    return results

def CalculateBestImage(sector):
    img_results = [CalculateImageDiff(sector.source_img, img)
                   for img in sector.image_list]
    unused_val, best_diff_idx = min((val, idx) for (idx, val) in
                                    enumerate(img_results))
    return SectorResult(sector.image_list[best_diff_idx], sector.x,
                        sector.y)

def CalculateImageDiff(source_img, image):
    diff = sum(map(CalculateDiff, source_img.pixel_list, image.pixel_list))
    return diff

def CalculateDiff(master, img):
    diff = abs(master[0] - img[0]) + abs(master[1] - img[1]) + abs(master[2] - img[2])
    return diff

def update_master_image(start_x, start_y, end_x, end_y, master_img, image_list):
    pool = Pool()
    sectors = []
    for x in range(start_x, end_x, indiv_size[0]):
        for y in range(start_y, end_y, indiv_size[1]):
            master_img_cropped = master_img.crop((x, y,
                                                  x + indiv_size[0],
                                                  y + indiv_size[1]))
            master_mosaic_img = MosaicImage(master_img_cropped)
            sector = Sector(master_mosaic_img, image_list, x, y)
            sectors.append(sector)
    map_results = pool.map_async(CalculateBestImage, sectors)
    sys.stdout.write(('Checking for best image in sectors: '
                      '(%d, %d) - (%d, %d)') % (start_x, start_y, end_x, end_y))
    print_map_async_status(map_results)
    img_results = map_results.get()
    [master_img.paste(sector.image.get_pil_image(), (sector.x, sector.y))
     for sector in img_results]
    pool.close()
    master_img.save('master_image.jpg', "JPEG")

def main():
    im = Image.open("%ssource.jpg" % IMAGE_DIR)
    master_img = im.resize(master_size, Image.ANTIALIAS)
    print('resized source image')
    image_list = get_image_list()
    for y in range(0, master_size[1], indiv_size[1]*4):
        update_master_image(0, y, master_size[0], y+(4*indiv_size[1]), master_img,
                            image_list)
        print('%d%% done' %(y/indiv_size[1]))
    print('build list of images and their pixels')
    master_img.save('master_image.jpg', "JPEG")

if __name__ == '__main__':
    main()


