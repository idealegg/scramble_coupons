# -*- coding: utf-8 -*-

import Get_Res.get_res as gr
from Util.image_util import *
import pytesseract


DEBUG=False
BEGIN_GET_INTERVAL = 0.01
IDENT_CODE_REFRESH_INTERVAL = 0.2
NO_CHECK=True

added=False

def add_warning_size():
    global added
    if not added:
        print(u"修改验证码位置")
        global INPUT_POS_TOP
        global INPUT_POS_BOTTOM
        global GET_POS_TOP
        global GET_POS_BOTTOM
        global IDENT_CODE_POS_TOP
        global IDENT_CODE_POS_BOTTOM
        INPUT_POS_TOP -= 40
        INPUT_POS_BOTTOM -= 40
        IDENT_CODE_POS_TOP -= 40
        IDENT_CODE_POS_BOTTOM -= 40
        GET_POS_TOP += 40
        GET_POS_BOTTOM += 40
    added = True

def roll_warning_size():
    global added
    if added:
        print(u"还原验证码位置")
        global INPUT_POS_TOP
        global INPUT_POS_BOTTOM
        global GET_POS_TOP
        global GET_POS_BOTTOM
        global IDENT_CODE_POS_TOP
        global IDENT_CODE_POS_BOTTOM
        INPUT_POS_TOP += 40
        INPUT_POS_BOTTOM += 40
        IDENT_CODE_POS_TOP += 40
        IDENT_CODE_POS_BOTTOM += 40
        GET_POS_TOP -= 40
        GET_POS_BOTTOM -= 40
    added = False

def get_begin():
    print(u"获取 立即领取 截图")
    img = get_snapshot()
    img = img.crop((BEGIN_POS_LEFT, 
                    BEGIN_POS_TOP, 
                    BEGIN_POS_RIGHT, 
                    BEGIN_POS_BOTTOM)) # left, top, right, bottom
    if 0:
        Image._show(img)
        input()
    res = check_img(img, u'立即领取', 240)
    rm_snapshot(img)
    print(u'立即领取已出现 => %s'%res)
    return res

def get_ident_code_img():
    while True:
        print(u"获取 验证码 截图")
        img = get_snapshot()
        #Image._show(img)
        img = img.crop((IDENT_CODE_POS_LEFT,
                        IDENT_CODE_POS_TOP,
                        IDENT_CODE_POS_RIGHT,
                        IDENT_CODE_POS_BOTTOM)) # left, top, right, bottom
        if not is_empty_code(img):
            return img
        print(u"未获取 验证码图片")
        if 0:
            print("等待%s秒刷新验证码" % IDENT_CODE_REFRESH_INTERVAL)
            time.sleep(IDENT_CODE_REFRESH_INTERVAL)


def verify_code(img, img_name=None, to_convert=True):
    if to_convert:
        img = gr.convert_img(img)
    result = ''
    for i in range(IDENT_CODE_CROP_BEGIN, IDENT_CODE_CROP_END, IDENT_CODE_CROP_STEP):
        img2 = img.crop((i, 0, i + IDENT_CODE_CROP_STEP, IDENT_CODE_POS_BOTTOM - IDENT_CODE_POS_TOP))
        # Image._show(img2)
        if not NO_CHECK and img_name:
            img2.save(os.path.join(gr.process_path, img_name.replace('.png', '_%s.png' % (i // 50,))))
        tmp = pytesseract.image_to_string(img2, lang='identcode', config='--psm 10')
        tmp = tmp.strip()
        if tmp:
            result += tmp[0]
    return result.strip().upper()

def get_ident_code():
    img = get_ident_code_img()
    #Image._show(img)
    img_name = get_img_name()
    store_path = os.path.join(gr.origin_path, img_name)
    if not NO_CHECK:
        img.save(store_path)
    if 1:
        result = verify_code(img, img_name)
    else:
        result = input("Please input code:")
    print("验证码结果: [%s]" % result)
    if result:
        print(u"输入验证码")
        click_input()
        #乱序问题，不要使用讯飞输入法，使用系统自带输入法
        input_text(result)
        roll_warning_size()
    res = False
    if len(result) != CHAR_NUM:
        res = False
    elif not DEBUG:
        print(u"点击领券")
        click_get()
        #time.sleep(0.5)
        rm_snapshot(img)
        while not NO_CHECK:
            img = get_snapshot()
            #Image._show(img)
            img2 = img.crop((GET_POS_LEFT,
                            GET_POS_TOP,
                            GET_POS_RIGHT,
                            GET_POS_BOTTOM))  # left, top, right, bottom
            #Image._show(img)
            res = not check_img(img2, u'领', 240)
            if res:
                img2 = img.crop((IDENT_CODE_POS_LEFT,
                                IDENT_CODE_POS_TOP,
                                IDENT_CODE_POS_RIGHT,
                                IDENT_CODE_POS_BOTTOM)) # left, top, right, bottom
                res2 = verify_code(img2)
                print("二次校验: %s" % res2)
                if len(res2) == 4 or set(result)&set(res2):
                    print(u"领券刷新中...")
                else:
                    break
                rm_snapshot(img)
            else:
                break
        print(u"领券成功" if res else u"领券失败")
        add_warning_size()
        #res = pytesseract.image_to_string(img, lang='chi_sim', config='--psm 7')
    else:
        res = input("验证码是否正确?{Y/N]")
        res = res[0].upper() == 'Y'
    #rm_snapshot(img)
    return res

def main():
    if not DEBUG:
        while not get_begin():
            if 0:
                print("等待%s秒"%BEGIN_GET_INTERVAL)
                time.sleep(BEGIN_GET_INTERVAL)
    start_time = time.time()
    print("点击 立即领取")
    click_begin()
    while not get_ident_code():
        if added:
            click_ident_code()
            if 0:
                print("等待%s秒刷新验证码" % IDENT_CODE_REFRESH_INTERVAL)
                time.sleep(IDENT_CODE_REFRESH_INTERVAL)
    end_time = time.time()
    print("用时: %.02f秒" % (end_time - start_time, ))

if __name__ == "__main__":
    main()