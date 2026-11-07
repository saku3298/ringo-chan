#!/usr/bin/env python3
"""work.json から、SNS共有用の画像（1200x630）を images/ogp/default.jpg に生成します。

必要なもの: Python 3、Pillow（pip install pillow）、日本語フォント
使い方（リポジトリのルートで）:
    python3 tools/make_ogp.py
フォントが見つからないときは、環境変数 OGP_FONT にフォントファイルのパスを指定してください。
    例) OGP_FONT="C:/Windows/Fonts/meiryo.ttc" python3 tools/make_ogp.py
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CANDIDATES = [
    os.environ.get("OGP_FONT", ""),
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "C:/Windows/Fonts/YuGothB.ttc",
    "C:/Windows/Fonts/meiryob.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
]
FONT = next((p for p in CANDIDATES if p and os.path.exists(p)), None)
if not FONT:
    sys.exit("日本語フォントが見つかりません。環境変数 OGP_FONT でフォントファイルを指定してください。")
REGULAR = FONT.replace("Bold", "Regular").replace("W8", "W3").replace("W6", "W3")
if not os.path.exists(REGULAR):
    REGULAR = FONT


def font(size, bold=True):
    return ImageFont.truetype(FONT if bold else REGULAR, size, index=0)


def find(base):
    for ext in ("webp", "jpg", "png"):
        if os.path.exists(f"{base}.{ext}"):
            return f"{base}.{ext}"
    sys.exit(f"画像が見つかりません: {base}.webp")


data = json.load(open("work.json", encoding="utf-8"))
work, episodes, volumes = data["work"], data["episodes"], data.get("volumes", [])
RED, INK, SUB, LINE = (239, 59, 53), (17, 17, 17), (119, 119, 119), (221, 221, 221)
W, H = 1200, 630

c = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(c)
d.rectangle((0, 0, W, 12), fill=RED)

if volumes:
    im = Image.open(find(f"images/pages/volume{volumes[0]['no']:02d}-001")).convert("RGB")
    h = 520
    w = int(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    x0, y0 = 90, 55
    sh = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((30, 36, 30 + w, 36 + h), fill=(0, 0, 0, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    c.paste(sh, (x0 - 30, y0 - 30), sh)
    bd = Image.new("RGB", (w + 4, h + 4), LINE)
    bd.paste(im, (2, 2))
    c.paste(bd, (x0 - 2, y0 - 2))
    tx = x0 + w + 70
else:
    tx = 90

d.text((tx, 100), "オリジナル漫画", font=font(30, False), fill=SUB)
size = 92
title = work["title"]
f = font(size)
while d.textlength(title, font=f) > W - tx - 60 and size > 40:
    size -= 4
    f = font(size)
d.text((tx, 160), title, font=f, fill=INK)
d.rectangle((tx, 160 + int(size * 1.35), tx + 110, 160 + int(size * 1.35) + 8), fill=RED)
d.text((tx, 160 + int(size * 1.35) + 40), f"作者：{work['author']}", font=font(36, False), fill=SUB)

n = len(episodes)
label = work.get("ogp_label") or (f"第{episodes[-1]['no']}話 公開中" if n == 1 else f"第{episodes[-1]['no']}話まで公開中")
lw = int(d.textlength(label, font=font(34))) + 56
ly = H - 150
d.rounded_rectangle((tx, ly, tx + lw, ly + 66), radius=33, fill=RED)
d.text((tx + 28, ly + 11), label, font=font(34), fill=(255, 255, 255))

os.makedirs("images/ogp", exist_ok=True)
c.save("images/ogp/default.jpg", quality=88, optimize=True)
print("生成: images/ogp/default.jpg")
