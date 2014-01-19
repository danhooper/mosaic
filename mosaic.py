#!/usr/bin/python
import datetime
from PIL import Image
import os
import sys

def main2():

    IMAGE_DIR = 'imgs/'
    master_size = (7200, 10800)
    indiv_size = (master_size[0]/50, master_size[1]/75)
    def get_image_list():
        image_dir_list = os.listdir('%s' % IMAGE_DIR)
        img_pix_list = []
        for file in image_dir_list:
            img = Image.open('%s%s' % (IMAGE_DIR, file))
            img = img.resize(indiv_size, Image.ANTIALIAS)
            img_pix = img.getdata()
            img_pix_list.append((img, img_pix))
        return img_pix_list



    def CalculateDiff(master, img):
        diff = abs(master[0] - img[0]) + abs(master[1] - img[1]) + abs(master[2] - img[2])
        return diff

    im = Image.open("%ssource.jpg" % IMAGE_DIR)
    master_img = im.resize(master_size, Image.ANTIALIAS)

    image_list = get_image_list()
    print (master_size[0], indiv_size[0])
    print (master_size[1], indiv_size[1])
    for x in range(0, master_size[0], indiv_size[0]):
        for y in range(0, master_size[1], indiv_size[1]):
            master_img_piece = master_img.crop((x, y, x + indiv_size[0], y + indiv_size[1]))
            master_img_pix = master_img_piece.getdata()
            best_diff = 32000000
            for image in image_list:
                diff_list = map(CalculateDiff, master_img_pix, image[1])
                diff = sum(diff_list)
                if diff < best_diff:
                    best_diff = diff
                    master_img.paste(image[0], (x, y))
            print (x, y, datetime.datetime.now())
            #sys.stdout.flush()
    master_img.save('master_image.jpg', "JPEG")


import cProfile
main2()


