# -*- coding: utf-8 -*-

import os
import Get_Res.get_res as gr


#os.chdir(r'Training')
if 0:
    cwd = os.getcwd()
    gr.run_cmd('tesseract identcode.normal.exp0.tif  identcode.normal.exp0 -l eng batch.nochop makebox')

    os.chdir(r'E:\Tesseract-OCR\jTessBoxEditor')
    os.system(r'E:\Tesseract-OCR\jTessBoxEditor\train.bat')
    os.chdir(cwd)

if 0:
    gr.run_cmd('tesseract identcode.normal.exp0.tif identcode.normal.exp0 --psm 7 nobatch box.train')
else:
    gr.run_cmd('tesseract identcode.normal.exp0.tif identcode.normal.exp0 nobatch box.train')

gr.run_cmd('unicharset_extractor identcode.normal.exp0.box')

with open('font_properties', 'wb') as fd:
    # 'font_name' 'italic' 'bold' 'fixed_pitch' 'serif' 'fraktur'
    fd.write(b'normal 0 1 1 0 0')

gr.run_cmd('shapeclustering -F font_properties -U unicharset identcode.normal.exp0.tr')

gr.run_cmd('mftraining -F font_properties -U unicharset -O unicharset identcode.normal.exp0.tr')

gr.run_cmd('cntraining identcode.normal.exp0.tr')

gr.run_cmd('mv normproto identcode.normproto')
gr.run_cmd('mv shapetable identcode.shapetable ')
gr.run_cmd('mv pffmtable identcode.pffmtable  ')
gr.run_cmd('mv inttemp identcode.inttemp  ')
gr.run_cmd('mv unicharset identcode.unicharset')

gr.run_cmd('combine_tessdata identcode.')

gr.run_cmd(r'cp identcode.traineddata E:\Tesseract-OCR\tessdata')

'''
在原有训练数据的基础上，如果有新的字符训练信息需要加入，所有数据重新校准一遍就累死人了。。。。

经研究找到实用合并方法（红色部分为示例，实际应为你自己生成的文件名）：

在新的训练数据生成.box 和.tr文件后，

生成字符集 unicharset_extractor add.font.exp0.box new.font.exp0.box

合并训练数据(.tr)

mftraining -F font_properties -U unicharset -O added.unicharset add.font.exp0.tr new.font.exp0.tr

聚合所有的tr文件：

cntraining add.font.exp0.tr new.font.exp0.tr

重命名文件，我把unicharset, inttemp, normproto, pfftable ，shapetable这几个文件加了前缀added.（注：added.只是我给合成的字典的命名，个人随意）

合并所有文件，生成一个大的资库文件。
'''