# -*- encoding: utf-8 -*-

import sys, math, os
from PIL import Image
from colorsys import rgb_to_hsv
from multiprocessing import Pool

IMAGES = '/Users/sam/Pictures/mosaic/'
IMAGE_SRC = '/Users/sam/Pictures/mosaic_src/'
IMAGE_DEST = '/Users/sam/Pictures/mosaic_dest/'

SLICE_WIDTH = 160
SLICE_HEIGHT = 90

DEST_IMAGE_WIDTH = 7680
DEST_IMAGE_HEIGHT = 4320

MAX_REPEAT = 10000

def process_images(image_dir):
    paths = []
    for filename in os.listdir(image_dir):
        if '.DS_Store' in filename:
            pass
        else:
            paths.append(image_dir + filename)
    pool = Pool()
    pool.map(process_image, paths)
    pool.close()
    pool.join()

def hsv_to_str(hsv):
    h, s, v = hsv[0], hsv[1], hsv[2]
    return str(h) + '_' + str(s) + '_' + str(v)

def process_image(image_path):
    image = Image.open(image_path)
    r_img = resize_image(image, SLICE_WIDTH, SLICE_HEIGHT)
    hsv = cal_hsv(r_img)
    r_img.save(IMAGE_SRC + hsv_to_str(hsv) + '.jpg')

def get_hsvlist(image_dir):
    hsv_list = []
    for filename in os.listdir(image_dir):
        if '.jpg' in filename:
            filename = filename.split('.jpg')[0]
            hsv = list(map(float, filename.split('_')))
            hsv.append(0)
            hsv_list.append(hsv)
    return hsv_list

def resize_image(image, width, height):
    return image.resize((width, height), Image.ANTIALIAS)

def cal_hsv(image):
    width, height = image.size
    count = width * height
    pixels = image.load()
    H = 0
    S = 0
    V = 0
    for w in range(width):
        for h in range(height):
            r, g, b = pixels[w, h]
            h, s, v = rgb_to_hsv(r / 255, g / 255, b / 255)
            H += h
            S += s
            V += v
    HAvg = round(H / count, 3)
    SAvg = round(S / count, 3)
    VAvg = round(V / count, 3)
    return HAvg, SAvg, VAvg

def find_closest(hsv, hsv_list):
    diff_min = sys.maxsize
    hsv_min = None
    for _hsv in hsv_list:
        diff = math.sqrt((hsv[0] - _hsv[0]) ** 2 + (hsv[1] - _hsv[1]) ** 2 + (hsv[2] - _hsv[2]) ** 2)
        if diff < diff_min and _hsv[3] < MAX_REPEAT:
            diff_min = diff
            hsv_min = _hsv
    if hsv_min:
        hsv_min[3] += 1
    else:
        raise Exception("请增大MAX_REPEAT的值或者增加图片数量")
    return IMAGE_SRC + hsv_to_str(hsv_min) + '.jpg'

def make_mosaic(image_ref):
    image = image_ref[1]
    image_tag = image_ref[0]
    print("正在处理图片：" + str(image_tag))
    hsv_list = get_hsvlist(IMAGE_SRC)
    width, height = image.size
    mosaic_img = Image.new('RGB', image.size, (255, 255, 255))
    # slice_counts = int((width * height) / (SLICE_WIDTH * SLICE_HEIGHT))
    for x1 in range(0, width, SLICE_WIDTH):
        for y1 in range(0, height, SLICE_HEIGHT):
            x2 = x1 + SLICE_WIDTH
            y2 = y1 + SLICE_HEIGHT
            slice = image.crop((x1, y1, x2, y2))
            hsv = cal_hsv(slice)
            closest_img = Image.open(find_closest(hsv, hsv_list))
            if closest_img.size[0] != SLICE_WIDTH or closest_img.size[1] != SLICE_HEIGHT:
                r_img = resize_image(closest_img, SLICE_WIDTH, SLICE_HEIGHT)
            else:
                r_img = closest_img
            mosaic_img.paste(r_img, (x1, y1, x2, y2))

    mosaic_img_blend = Image.blend(mosaic_img, image, 0.5)

    mosaic_img.save(IMAGE_DEST + 'source_' + str(image_tag) + 'mosaic_' + str(MAX_REPEAT) + '.jpg')
    mosaic_img_blend.save(IMAGE_DEST + 'source_' + str(image_tag) + 'mosaic_blend_' + str(MAX_REPEAT) + '.jpg')
    print("成功处理图片：" + str(image_tag))

def show_mosaic_process(image_ref):
    image = image_ref[1]
    image_tag = image_ref[0]
    print("正在处理图片：" + str(image_tag))
    hsv_list = get_hsvlist(IMAGE_SRC)
    width, height = image.size
    mosaic_img = Image.new('RGB', image.size, (255, 255, 255))
    slice_num = 0
    for x1 in range(0, width, SLICE_WIDTH):
        for y1 in range(0, height, SLICE_HEIGHT):
            x2 = x1 + SLICE_WIDTH
            y2 = y1 + SLICE_HEIGHT
            slice = image.crop((x1, y1, x2, y2))
            hsv = cal_hsv(slice)
            closest_img = Image.open(find_closest(hsv, hsv_list))
            if closest_img.size[0] != SLICE_WIDTH or closest_img.size[1] != SLICE_HEIGHT:
                r_img = resize_image(closest_img, SLICE_WIDTH, SLICE_HEIGHT)
            else:
                r_img = closest_img
            mosaic_img.paste(r_img, (x1, y1, x2, y2))
            slice_num += 1

            mosaic_img.save(IMAGE_DEST + str(slice_num) + '.jpg')

    mosaic_img_blend = Image.blend(mosaic_img, image, 0.5)

    mosaic_img.save(IMAGE_DEST + 'total.jpg')
    mosaic_img_blend.save(IMAGE_DEST + 'total_blend.jpg')
    print("成功处理图片：" + str(image_tag))

if __name__ == '__main__':
    # process_images(IMAGES)
    # image_list = []
    #
    # pool = Pool()
    # for i in range(1, 5):
    #     img_path = IMAGES + 'source_' + str(i) + '.JPG'
    #
    #     source_image = Image.open(img_path)
    #     r_img = resize_image(source_image, DEST_IMAGE_WIDTH, DEST_IMAGE_HEIGHT)
    #     r_img.save(IMAGE_DEST + str(i) + 'r_img.jpg')
    #     image_list.append((i, r_img))
    # print("开始处理图片")
    # pool.map(make_mosaic, image_list)
    # pool.close()
    # pool.join()
    # print("成功处理图片")

    img_path = IMAGES + 'source_' + str(1) + '.JPG'

    source_image = Image.open(img_path)
    r_img = resize_image(source_image, DEST_IMAGE_WIDTH, DEST_IMAGE_HEIGHT)

    show_mosaic_process((1, r_img))
