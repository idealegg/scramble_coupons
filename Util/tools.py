# -*- coding: utf-8 -*-

import os
from aip import AipOcr


APP_ID='21293501'
API_KEY ='yP0NOscIXVmRXClx29czHNG2'
SECRET_KEY ='2zchq1UaKzqNFGt8NW2KOXT7E2GlrqZx'


client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
options = {
   "language_type" : "CHN_ENG",
   "recognize_granularity" : "big",
   "detect_direction" : "true",
   "vertexes_location" : "true",
   "probability" : "true"
}


def run_cmd(cmd, to_print=False, to_close=True):
    fd = os.popen(cmd)
    out = fd.read()
    if to_print:
        print("cmd: [%s]" % cmd)
        print(out)
    if to_close:
        fd.close()

def check_word(img_stream, word):
    #text = client.basicGeneral(stream.getvalue(), options)
    """ 带参数调用通用文字识别（含位置高精度版） """
    #text = client.accurate(stream.getvalue(), options)
    text = client.basicAccurate(img_stream.getvalue(), options)
    for i in text['words_result']:
        #if i['words'] == u'立即领取':
        if i['words'] == word:
            return  True
    return False

def transfer_png_2_tif():
    import os
    os.chdir(r'D:\pycharmProject\scramble_coupons\res\old')
    from PIL import Image
    for f in os.listdir('.'):
        if f.endswith('png'):
            im = Image.open(f)
            im.save(f.replace('png', 'tif'))
            os.unlink(f)
