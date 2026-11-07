#!/usr/bin/env python3
"""images/ の画像を WebP に変換して、容量を軽くします（見た目はほぼ変わりません）。

対象: images/ 以下の *.jpg / *.jpeg / *.png（images/ogp/ は除く）
必要なもの: Python 3 と Pillow（pip install pillow）
使い方（リポジトリのルートで）:
    python3 tools/optimize_images.py                     # WebPを作る（元の画像は残す）
    python3 tools/optimize_images.py --delete-originals  # 変換できたら元の画像を消す

画像を追加したら、これを実行してから tools/build.py を実行してください。
ファイルの末尾が欠けたJPEGは、警告を出したうえで読める範囲で変換します。
"""
import glob, os, sys
from PIL import Image, ImageFile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
QUALITY = 85
delete = "--delete-originals" in sys.argv

targets = []
for ext in ("jpg", "jpeg", "png"):
    targets += [p for p in glob.glob(f"images/**/*.{ext}", recursive=True)
                if not p.replace("\\", "/").startswith("images/ogp/")]

before = after = 0
for src in sorted(targets):
    dst = os.path.splitext(src)[0] + ".webp"
    try:
        im = Image.open(src)
        im.load()
    except OSError:
        print(f"警告: {src} は末尾が欠けています。読める範囲で変換します（元ファイルの確認をおすすめします）")
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        im = Image.open(src)
        im.load()
        ImageFile.LOAD_TRUNCATED_IMAGES = False
    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    before += os.path.getsize(src)
    after += os.path.getsize(dst)
    print(f"変換: {src} -> {os.path.basename(dst)}")
    if delete:
        os.remove(src)

if targets:
    print(f"\n{len(targets)}枚: {before/1e6:.2f}MB -> {after/1e6:.2f}MB（{after/before:.0%}）")
else:
    print("変換する画像はありませんでした。")
