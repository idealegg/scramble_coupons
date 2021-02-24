# -*- coding: utf-8 -*-

from Util.image_util import *


def get_img():
    img = get_snapshot()
    img_name = get_img_name()
    img = img.crop((IDENT_CODE_POS_LEFT, IDENT_CODE_POS_TOP, IDENT_CODE_POS_RIGHT, IDENT_CODE_POS_BOTTOM)) # left, top, right, bottom
    #Image._show(img)
    img.save(os.path.join(origin_path, img_name))
    img = convert_img(img)
    img.save(os.path.join(process_path, img_name))
    rm_snapshot(img)


def main():
    while True:
        get_img()
        run_cmd('adb shell input tap %s %s' % ( (IDENT_CODE_POS_LEFT + IDENT_CODE_POS_RIGHT) // 2,
                                                 (IDENT_CODE_POS_TOP + IDENT_CODE_POS_BOTTOM) // 2))
        time.sleep(TAP_INTERVAL + random.randrange(0, 500) / 1000)


if __name__ == '__main__':
    main()
