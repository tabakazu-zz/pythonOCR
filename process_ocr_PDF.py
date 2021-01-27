from PIL import Image
import sys
import pyocr
import pyocr.builders
from pdf2image import convert_from_path
import re
import subprocess
import os
from pathlib import Path

tools = pyocr.get_available_tools()
tool = tools[0]
langs = tool.get_available_languages()
print("Available languages: %s" % ", ".join(langs))
lang = langs[1]
print("Will use lang '%s'" % (lang))

# 対象PDFファイル名
Nm = 'vyvo(raw)'

# 配置先ディレクトリ
pdf_path = Path("./pdf_file/" + Nm + ".pdf")
txt_path = Path("./txt_file/" + Nm + ".txt")
out_path = Path("./pdf_file/output/" + Nm + ".pdf")

# PDF -> pagesにImageとして変換する（300dpi指定）
# dpiは無意味かも
pages = convert_from_path(str(pdf_path), 300)

txt = ''
for i, page in enumerate(pages):
    txt = txt + tool.image_to_string(page, lang='jpn', builder=pyocr.builders.TextBuilder(tesseract_layout=6))
    txt = re.sub('([あ-んア-ン一-龥ー])\s+((?=[あ-んア-ン一-龥ー]))', r'\1\2', txt)

# テキストファイル出力
s = txt
with open(txt_path, mode='w') as f:
    f.write(s)

# マルチページのTIFFとして保存する
image_dir = Path("./image_file")
tiff_name = pdf_path.stem + ".tif"
image_path = image_dir / tiff_name
to_pdf = pdf_path.stem + "_TO"
topdf_path = image_dir / to_pdf

# 既存ファイル削除
if os.path.exists(image_path):
    os.remove(image_path)
if os.path.exists(str(topdf_path) + '.pdf'):
    os.remove(str(topdf_path) + '.pdf')

pages[0].save(str(image_path), "TIFF", compression="tiff_deflate", save_all=True, append_images=pages[1:])

# テキストオンリーpdfの生成
cmd = 'tesseract -c page_separator="[PAGE SEPRATOR]" -c textonly_pdf=1 "' + str(image_path) + '" "' + str(
    topdf_path) + '" -l jpn pdf'
print(cmd)
returncode = subprocess.Popen(cmd, shell=True)
returncode.wait()

# オリジナルのpdfにtextonlyのpdfをオーバーレイして最小サイズのpdfを生成してみる。qpdfの基本コマンドは以下
# to.pdf＝テキストオンリーpdf　org.pdf＝オリジナルpdf　out.pdf=オーバレイ済pdf
# qpdf --overlay to.pdf -- org.pdf out.pdf
if os.path.exists(out_path):
    print('remove　' + out_path)
    os.remove(out_path)
cmd = 'qpdf --overlay "' + str(topdf_path) + '.pdf" -- "' + str(pdf_path) + '" "' + str(out_path) + '" '
print(cmd)
returncode = subprocess.Popen(cmd, shell=True)
returncode.wait()