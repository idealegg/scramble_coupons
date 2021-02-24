# -*- coding: utf-8 -*-

import os
from PIL import Image
import time
import random
from Util.tools import run_cmd, check_word
from io import BytesIO
import pytesseract


GRAY_THRESHOLD=150
TRUNCATE_WIDTH=5
TAP_INTERVAL = 2.0
EMPTY_THREHOLD = 240
CHAR_NUM = 4


BEGIN_POS_LEFT = 380
BEGIN_POS_TOP = 500 + 80
BEGIN_POS_RIGHT = 700
BEGIN_POS_BOTTOM = 600 + 80

# INPUT  IDENT_CODE
# prompt
#      GET

INPUT_POS_LEFT = 130
INPUT_POS_TOP = 990
INPUT_POS_RIGHT = 670
INPUT_POS_BOTTOM = 1090

IDENT_CODE_POS_LEFT = 690
IDENT_CODE_POS_TOP = 990
IDENT_CODE_POS_RIGHT = 950
IDENT_CODE_POS_BOTTOM = 1090

GET_POS_LEFT = 380
GET_POS_TOP = 1160
GET_POS_RIGHT = 700
GET_POS_BOTTOM = 1260

IDENT_CODE_CROP_BEGIN = 30
IDENT_CODE_CROP_STEP = 53
IDENT_CODE_CROP_END = IDENT_CODE_CROP_BEGIN + CHAR_NUM * IDENT_CODE_CROP_STEP


res_dir=r'res'
shot_png = '01.png'
shot_dir = '/sdcard'
shot_path = "%s/%s" % (shot_dir, shot_png)
origin_path = os.path.join(res_dir, 'origin')
process_path = os.path.join(res_dir, 'processed')
shot_png2 = '02.png'
shot_dir = '/sdcard'
shot_path2 = "%s/%s" % (shot_dir, shot_png2)


time_map = {}


def get_snapshot():
    run_cmd('adb shell screencap -p %s'  % shot_path)
    run_cmd('adb pull %s' % (shot_path, ))
    return Image.open(shot_png)

def rm_snapshot(img=None):
    if img:
        img.close()
    os.remove(shot_png)
    run_cmd('adb shell rm %s' % shot_path)

def convert_img(img):
    img = img.convert("L")  # 处理灰度
    pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            if pixels[x, y] > GRAY_THRESHOLD:
                pixels[x, y] = 255
            else:
                pixels[x, y] = 0
    data = img.getdata()
    w, h = img.size
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            # 找出各个像素方向
            mid_pixel = data[w * y + x]
            top_pixel = data[w * (y - 1) + x]
            left_pixel = data[w * y + (x - 1)]
            down_pixel = data[w * (y + 1) + x]
            right_pixel = data[w * y + (x + 1)]
            count = (top_pixel + left_pixel + down_pixel + right_pixel) // 255
            if mid_pixel == 255 and count <= 1:
                img.putpixel((x, y), 0)
                #print("mid_pixel: %s, count: %s, x: %s, y: %s" % (mid_pixel, count, x, y))
            elif mid_pixel == 0 and count >= 3:
                img.putpixel((x, y), 255)
                #print("mid_pixel: %s, count: %s, x: %s, y: %s" % (mid_pixel, count, x, y))
    for x in range(0, w - 1):
        for y in range(0, h - 1):
            # 找出各个像素方向
            mid_pixel = data[w * y + x]
            if mid_pixel == 0:
                count = 1
                for i in range(1, TRUNCATE_WIDTH):
                    if y - i > 0 and data[w * (y - i) + x] == 0:
                        count += 1
                    if y + i < h and data[w * (y + i) + x] == 0:
                        count += 1
                    if count >= TRUNCATE_WIDTH:
                        break
                if count < TRUNCATE_WIDTH:
                    img.putpixel((x, y), 255)
                    #print("count: %s, x: %s, y: %s" % (count, x, y))
                    continue
                count = 1
                for i in range(1, TRUNCATE_WIDTH):
                    if x - i > 0 and data[w * y + x - i] == 0:
                        count += 1
                    if x + i < w and data[w * y + x + i] == 0:
                        count += 1
                    if count >= TRUNCATE_WIDTH:
                        break
                if count < TRUNCATE_WIDTH:
                    img.putpixel((x, y), 255)
                    #print("count: %s, x: %s, y: %s" % (count, x, y))
    return img

def convert_img2(im, store_path):
    width, height = im.size
    # 获取图片中的颜色，返回列表[(counts, color)...]
    color_info = im.getcolors(width * height)
    # 按照计数从大到小排列颜色，那么颜色计数最多的应该是背景，接下来排名2到6的则对应5个字符。
    sort_color = sorted(color_info, key=lambda x: x[0], reverse=True)
    # 根据颜色，提取出每一个字符，重新放置到一个新建的白色背景image对象上。每个image只放一个字符。
    char_dict = {}
    for i in range(1, 5):
        im2 = Image.new('RGB', im.size, (255, 255, 255))
        for x in range(width):
            for y in range(height):
                if im.getpixel((x, y)) == sort_color[i][1]:
                    im2.putpixel((x, y), (0, 0, 0))
                else:
                    im2.putpixel((x, y), (255, 255, 255))
        im2.save("".join([store_path.replace('.png', ''), '_%s'%i, '.tif']))
    print('成功处理图片{}'.format(store_path))


def convert_img3(img, threhold=GRAY_THRESHOLD):
    img = img.convert("L")  # 处理灰度
    pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            if pixels[x, y] > threhold:
                pixels[x, y] = 0
            else:
                pixels[x, y] = 255
    return img


def get_img_name(ext='png'):
    time_inf = time.strftime('%Y-%m-%d_%H-%M-%S')
    time_map[time_inf] = 0 if time_inf not in time_map else time_map[time_inf] + 1
    return '%s_%s.%s' % (time_inf, time_map[time_inf], ext)


def check_img(img, word, threhold=GRAY_THRESHOLD):
    img = convert_img3(img, threhold)
    #Image._show(img)
    result = pytesseract.image_to_string(img, lang='chi_sim', config='--psm 7')
    result = result.strip().replace(' ', '')
    print('check_img: [%s]' % result)
    return result.count(word)


def check_img2(img, word):
    stream = BytesIO()
    img.save(stream, "png")
    return check_word(stream, word)

def click_pos(pos): # left, top, right, bottom
    run_cmd('adb shell input tap %s %s' % ((pos[0] + pos[2]) // 2,
                                                   (pos[1] + pos[3]) // 2))

def click_begin():
    click_pos((BEGIN_POS_LEFT,
               BEGIN_POS_TOP,
               BEGIN_POS_RIGHT,
               BEGIN_POS_BOTTOM))
    
def click_input():
    click_pos((INPUT_POS_LEFT,
               INPUT_POS_TOP,
               INPUT_POS_RIGHT,
               INPUT_POS_BOTTOM))
    
def click_ident_code():
    click_pos((IDENT_CODE_POS_LEFT,
               IDENT_CODE_POS_TOP,
               IDENT_CODE_POS_RIGHT,
               IDENT_CODE_POS_BOTTOM))
    
def click_get():
    click_pos((GET_POS_LEFT,
               GET_POS_TOP,
               GET_POS_RIGHT,
               GET_POS_BOTTOM))

def input_text(text):
    run_cmd('adb shell input text %s' % text)

def get_ave_l(f):
    img=Image.open(f)
    img=img.convert('L')
    sum=0
    count=0
    width, height = img.size
    color_info = img.getcolors(width * height)
    for i in color_info:
            sum += i[0] * i[1]
            count += i[0]
    print(sum/count)

'''>>> for f in os.listdir('.'):
...     get_ave_l(f)
...
211.12603846153846
199.89765384615384
202.43392307692307
208.81334615384614
194.76607692307692
210.5111923076923
200.38753846153847
200.13465384615384
210.18030769230768
197.51642307692308
203.5841153846154
205.4431923076923
203.79346153846154
196.82526923076924
204.21253846153846
205.43407692307693
206.0561153846154
199.3856153846154
245.1798076923077
245.1798076923077
245.1798076923077
198.8865
245.1798076923077
200.9343846153846'''


def is_empty_code(img):
    img=img.convert('L')
    sum=0
    count=0
    width, height = img.size
    color_info = img.getcolors(width * height)
    for i in color_info:
            sum += i[0] * i[1]
            count += i[0]
    return sum/count > EMPTY_THREHOLD