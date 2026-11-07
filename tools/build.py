#!/usr/bin/env python3
"""work.json から、このサイトのHTMLをすべて生成します。

使い方（リポジトリのルートで）:
    python3 tools/build.py

生成されるもの:
    index.html（作品トップ）、illustrations.html（イラスト集）、
    episodes/episodeNN.html（各話）、volumes/volumeNN.html（単行本）、
    reader.html（昔のURL用の転送ページ）、404.html

編集してよいのは work.json、css/、js/ です。生成されたHTMLは直接編集しないでください。

画像の置き場所（既存の画像はそのまま使います）:
    images/pages/episodeNN-PPP.jpg   各話のページ（話2桁-ページ3桁。webpでも可）
    images/pages/volumeNN-001.jpg など 単行本の表紙・目次・巻末ページ
    images/thumbs/episodeNN.jpg      話一覧のサムネイル
    images/thumbs/volumeNN.jpg       コミックス一覧・トップの表紙
    images/illustrations/illustration-001.jpg  イラスト集
    images/related/                  「同じ作者の作品」の表紙

新しい話を追加するとき:
  1. 画像を置く（上の命名規則）
  2. work.json の "episodes" に { "no": 83, "title": "…" } を足し、
     該当する巻の "layout" に 83 を足す（新しい巻は "volumes" に追加）
  3. python3 tools/build.py
ページ数は画像の枚数から自動で数えます。
"""
import glob, hashlib, html, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
e = html.escape

data = json.load(open("work.json", encoding="utf-8"))
site, work = data["site"], data["work"]
episodes, volumes = data["episodes"], data.get("volumes", [])
related, site_link, illus = data.get("related", []), data.get("site_link"), data.get("illustrations")
BASE = site["url"].rstrip("/") + "/"
TITLE = work["title"]
PER_RANGE = 50


def ver(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()[:8]


def img(base):
    """拡張子なしのパスから、実在する画像（webp優先）のパスを返す"""
    for ext in ("webp", "jpg", "png"):
        if os.path.exists(f"{base}.{ext}"):
            return f"{base}.{ext}"
    sys.exit(f"エラー: 画像が見つかりません: {base}.jpg（または .webp）")


def episode_files(no):
    """images/pages/episodeNN-*.* をページ順に返す（拡張子なし）"""
    stems = set()
    for ext in ("webp", "jpg", "png"):
        for p in glob.glob(f"images/pages/episode{no:02d}-*.{ext}"):
            stems.add(os.path.splitext(os.path.basename(p))[0])
    if not stems:
        sys.exit(f"エラー: images/pages/episode{no:02d}-001.jpg などがありません")
    return sorted(stems)


ep_files = {ep["no"]: episode_files(ep["no"]) for ep in episodes}
ep_by_no = {ep["no"]: ep for ep in episodes}
vol_of_ep = {}
for v in volumes:
    for item in v["layout"]:
        if isinstance(item, int):
            vol_of_ep[item] = v


def volume_files(v):
    out = []
    for item in v["layout"]:
        out += ep_files[item] if isinstance(item, int) else [item]
    return out


V_CSS = ver("css/style.css")
V_VIEWER = ver("js/viewer.js")
V_TOP = ver("js/top.js")


def head(title, desc, url, typ, prefix="", extra_css="", theme=False, main_css=True):
    return f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{'<meta name="theme-color" content="#111111">' if theme else ''}
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{typ}">
<meta property="og:site_name" content="{e(site["name"])}">
<meta property="og:locale" content="ja_JP">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}images/ogp/default.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(TITLE)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
{f'<link rel="stylesheet" href="{prefix}css/style.css?v={V_CSS}">' if main_css else ''}{extra_css}</head>
'''


def index_page():
    first, last = episodes[0], episodes[-1]
    n_ep, n_vol = len(episodes), len(volumes)
    cover1 = img(f"images/thumbs/volume{volumes[0]['no']:02d}")
    ranges = ""
    if n_ep > PER_RANGE:
        btns = []
        for s in range(1, n_ep + 1, PER_RANGE):
            act = s == 1
            btns.append(f'<button aria-pressed="{str(act).lower()}" class="episode-range-btn{" active" if act else ""}" '
                        f'data-range-end="{s + PER_RANGE - 1}" data-range-start="{s}" type="button">{s}-{min(s + PER_RANGE - 1, n_ep)}</button>')
        ranges = f'<div aria-label="話数範囲" class="episode-range-tabs" role="group">{"".join(btns)}</div>'
    rows = "".join(
        f'<a class="episode-row" data-episode="{ep["no"]}" href="episodes/episode{ep["no"]:02d}.html"{" hidden" if ep["no"] > PER_RANGE else ""}>'
        f'<img alt="第{ep["no"]}話扉絵" src="{img(f"images/thumbs/episode{ep["no"]:02d}")}"/>'
        f'<strong>第{ep["no"]}話 {e(ep["title"])}</strong><span class="episode-read">読む</span></a>' for ep in episodes)
    ents = ""
    for v in volumes:
        n = v["no"]
        pages = len(volume_files(v))
        ents += (f'<a class="entry" data-volume="{n}" href="volumes/volume{n:02d}.html"><img alt="第{n}巻表紙" src="{img(f"images/thumbs/volume{n:02d}")}"/>'
                 f'<span><strong>第{n}巻</strong><small>全{pages}ページ・第{v["episodes"][0]}〜{v["episodes"][-1]}話収録</small><em>読む</em></span></a>')
    tab = ' target="_blank" rel="noopener"'
    cards = "".join(
        f'<a class="author-work-card" href="{e(r["url"])}"{tab if r.get("new_tab") else ""}>'
        f'<img alt="{e(r["cover_alt"])}" src="images/related/{r["cover"]}"/>'
        f'<div><div class="author-work-title">{e(r["title"])}</div><div class="author-work-author">作者：{e(r["author"])}</div>'
        f'<span class="author-work-label">コミックス</span></div></a>' for r in related)
    if site_link:
        cards += (f'<a class="author-work-card" href="{e(site_link["url"])}"{tab if site_link.get("new_tab") else ""}>'
                  f'<img alt="{e(site_link["title"])}" src="images/related/{site_link["image"]}"/>'
                  f'<div><div class="author-work-title">{e(site_link["title"])}</div>'
                  f'<div class="author-work-author">{e(site_link["description"])}</div>'
                  f'<span class="author-work-label">作品集</span></div></a>')
    related_html = f'<div class="related-works info-section"><h2>同じ作者の作品</h2>{cards}</div>' if cards else ""
    illus_html = ""
    if illus:
        illus_html = (f'<div class="info-section illustration-gallery-section"><h2>イラスト集</h2>'
                      f'<a class="illustration-gallery-link" href="illustrations.html">'
                      f'<img alt="{e(illus["title"])}の表紙" src="{img("images/illustrations/illustration-%03d" % illus["cover"])}"/>'
                      f'<div><strong>{e(illus["title"])}</strong><p>{e(illus["summary"])}</p><span>イラスト集を見る ›</span></div></a></div>')
    return head(f'{TITLE} | {work["author"]}', site["description"], BASE, "website") + f'''<body><main class="shell"><header><img alt="{e(TITLE)} 第1巻表紙" class="hero" src="{cover1}"/><h1>{e(TITLE)}</h1><p>作者：{e(work["author"])}</p><div class="hero-actions"><a class="primary" href="episodes/episode{first["no"]:02d}.html">第{first["no"]}話から読む</a><a class="secondary-action" href="episodes/episode{last["no"]:02d}.html">最新話から読む</a></div></header><nav><button class="active" data-tab="episodes">話</button><button data-tab="volumes">コミックス</button><button data-tab="about">作品情報</button></nav><section class="panel active episode-list" data-per-range="{PER_RANGE}" id="episodes"><div class="episode-summary"><span>全{n_ep}話</span><div><button class="sort-btn active" data-order="asc" data-sort="episode" type="button">1話から</button><span>｜</span><button class="sort-btn" data-order="desc" data-sort="episode" type="button">最新話から</button></div></div>{ranges}<a class="latest-episode-action" href="episodes/episode{last["no"]:02d}.html">最新話 第{last["no"]}話を読む</a>{rows}</section><section class="panel" id="volumes"><div class="volume-summary"><span>全{n_vol}巻</span><div><button class="sort-btn active" data-order="asc" data-sort="volume" type="button">1巻から</button><span>｜</span><button class="sort-btn" data-order="desc" data-sort="volume" type="button">最新巻から</button></div></div><a class="latest-volume-action" href="volumes/volume{volumes[-1]["no"]:02d}.html">最新巻 第{volumes[-1]["no"]}巻を読む</a>{ents}</section><section class="panel info" id="about"><h2>作品情報</h2><p>作品名：{e(TITLE)}</p><p>作者：{e(work["author"])}</p><p>連載状況：{e(work["status"])}</p>{illus_html}{related_html}</section></main><script src="js/top.js?v={V_TOP}"></script></body></html>
'''


def pages_html(items, eager):
    out = []
    for i, (src, alt) in enumerate(items):
        lazy = "" if i < eager else ' loading="lazy"'
        out.append(f'<div class="manga-page"><img{lazy} src="../images/pages/{src}" alt="{e(alt)}"></div>')
    return "".join(out)


def reader_page(title, page_title, desc, url, files, vol, volume_reader, back_href, back_text):
    items = [(img("images/pages/" + f).split("/", 2)[2], f"{title} ページ{i + 1}") for i, f in enumerate(files)]
    vattr = f' data-volume-href="../volumes/volume{vol["no"]:02d}.html" data-volume-label="第{vol["no"]}巻"' if vol else ""
    return (head(page_title, desc, url, "article", prefix="../", theme=True)
            + f'<body class="reader-page"><header class="reader-bar"><div class="reader-bar-inner"><div class="reader-title"><a href="{back_href}" id="context-back">{back_text}</a> <span id="reader-title">{e(title)}</span></div>'
              f'<div class="reader-controls"><button class="small-btn" id="top" type="button">先頭へ</button></div></div>'
              f'<div class="progress" aria-hidden="true"><div id="progress-fill"></div></div></header>'
              f'<main class="viewer" data-volume-reader="{str(volume_reader).lower()}"{vattr} id="viewer">{pages_html(items, 3)}</main>'
              f'<div class="page-nav"><button id="prev" type="button">← 次のページ</button><button id="next" type="button">前のページ →</button></div>'
              f'<div class="counter" id="counter">1 / {len(files)}</div>'
              f'<div class="reader-footer"><a href="../index.html">作品トップへ戻る</a></div>'
              f'<script src="../js/viewer.js?v={V_VIEWER}"></script></body></html>\n')


def episode_page(ep):
    no = ep["no"]
    title = f'第{no}話 {ep["title"]}'
    return reader_page(title, f'{title} | {TITLE}', f'オリジナル漫画『{TITLE}』{title}',
                       f"{BASE}episodes/episode{no:02d}.html", ep_files[no], vol_of_ep.get(no), False,
                       "../index.html", "← 作品トップへ")


def volume_page(v):
    no = v["no"]
    title = f'第{no}巻'
    return reader_page(title, f'{title} | {TITLE}', f'オリジナル漫画『{TITLE}』{title}',
                       f"{BASE}volumes/volume{no:02d}.html", volume_files(v), None, v.get("spread_from_cover", True),
                       "../index.html#volumes", "← 作品トップへ")


def illustrations_page():
    d = f'data-groups="{e(json.dumps(illus["groups"]))}" data-total="{illus["count"]}" data-base="images/illustrations/"'
    return (head(f'{illus["title"]} | {TITLE}', f'{TITLE}のイラスト集（全{illus["count"]}ページ）', f"{BASE}illustrations.html", "article",
                 extra_css=f'<link rel="stylesheet" href="css/illustrations.css?v={ver("css/illustrations.css")}">', main_css=False)
            + f'''<body><header><a href="index.html#about">‹ 作品情報に戻る</a><strong>{e(illus["title"])}</strong></header>
<main><div id="spread" aria-live="polite" {d}></div></main>
<footer><button id="next" type="button">次へ</button><span id="counter"></span><button id="prev" type="button">前へ</button></footer>
<script src="js/illustrations.js?v={ver("js/illustrations.js")}"></script></body></html>
''')


def redirect_page():
    """昔のURL（reader.html?mode=episode3 など）から新しいページへ転送する"""
    return f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>{e(TITLE)}</title></head>
<body><p><a href="index.html">作品トップへ</a></p>
<script>
(function(){{var q=new URLSearchParams(location.search),m=q.get('mode')||'volume',x=/^episode(\\d+)$/.exec(m),y=/^volume(\\d*)$/.exec(m),t='index.html';
if(x)t='episodes/episode'+('0'+x[1]).slice(-2)+'.html';else if(y)t='volumes/volume'+('0'+(y[1]||'1')).slice(-2)+'.html';
if(q.get('from'))t+=(t.indexOf('?')<0?'?':'&')+'from='+encodeURIComponent(q.get('from'));
location.replace(t)}})();
</script></body></html>
'''


def not_found_page():
    return f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>ページが見つかりません | {e(TITLE)}</title>
<link rel="icon" href="{BASE}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{BASE}css/style.css?v={V_CSS}"></head>
<body><main class="shell"><div class="nf">
<p class="nf-code" aria-hidden="true">404</p>
<h1>ページが見つかりません</h1>
<p>URLがまちがっているか、ページが移動したのかもしれません。</p>
<a class="nf-btn" href="{BASE}">{e(TITLE)}のトップへ</a>
</div></main></body></html>
'''


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(text)


write("index.html", index_page())
if illus:
    write("illustrations.html", illustrations_page())
for ep in episodes:
    write(f"episodes/episode{ep['no']:02d}.html", episode_page(ep))
for v in volumes:
    write(f"volumes/volume{v['no']:02d}.html", volume_page(v))
write("reader.html", redirect_page())
write("404.html", not_found_page())
print(f"完了: index.html, illustrations.html, 話{len(episodes)}・巻{len(volumes)}, reader.html, 404.html")
