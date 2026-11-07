# りんごちゃん

れ。作のオリジナル漫画『りんごちゃん』（全82話・休載中）の公開サイトです（GitHub Pages）。
公開URL: https://saku3298.github.io/ringo-chan/

画面はジャンププラス風です（リカリカイと同じデザイン）。縦向きは1ページ表示、横向きは右から左の2ページ見開きで読めます。

## フォルダ構成

| 場所 | 役割 |
|---|---|
| `work.json` | 作品情報・話数・巻・イラスト集・関連作品のデータ（**ここを編集します**） |
| `tools/build.py` | `work.json` から全HTMLを生成します |
| `tools/make_ogp.py` | SNS共有用の画像を `images/ogp/default.jpg` に生成します |
| `tools/optimize_images.py` | 画像をWebPに変換します（新しく追加した画像にだけ使います） |
| `css/style.css` | 画面のデザイン（トップ・ビューア・404。リカリカイと共通の骨格） |
| `css/illustrations.css` | イラスト集のデザイン |
| `js/viewer.js` | ビューア（スワイプ・見開き・続きから読む・進捗バー） |
| `js/top.js` | トップページ（タブ・話数の範囲と並べ替え） |
| `js/illustrations.js` | イラスト集ビューア |
| `images/pages/` | 各話のページ `episodeNN-PPP.jpg`、単行本の表紙・目次・巻末 `volumeNN-…jpg` |
| `images/thumbs/` | 話一覧 `episodeNN.jpg`・コミックス一覧 `volumeNN.jpg` のサムネイル |
| `images/illustrations/` | イラスト集 `illustration-001.jpg` … |
| `images/related/` | 「同じ作者の作品」の表紙 |
| `images/work/` | トップのヒーロー画像 `hero-panel.jpg` |
| `images/ogp/` | SNS共有用の画像 |
| `assets/favicon.svg` | タブのアイコン |
| `index.html`, `illustrations.html`, `episodes/`, `volumes/`, `404.html`, `reader.html` | **自動生成されるので直接編集しません** |

`reader.html` は、昔のURL（`reader.html?mode=episode3` など）を新しいページへ転送するためのものです。昔のリンクが不要になれば削除して構いません（`tools/build.py` を実行すると再び作られるので、不要なら `build.py` の `reader.html` の行も消してください）。

## 新しい話を追加する手順（第83話の例）

1. 画像を置く
   - 本文: `images/pages/episode83-001.jpg`, `episode83-002.jpg` …（話2桁-ページ3桁。WebPでも可）
   - サムネイル: `images/thumbs/episode83.jpg`
2. `work.json` を編集する
   - `episodes` に `{ "no": 83, "title": "タイトル" }` を足す
   - 単行本に入れるなら、その巻の `layout` に `83` を足す（巻末ページなどはファイル名を並べます）
   - 新しい巻なら `volumes` に追加し、`images/pages/volume12-001.jpg`（表紙）と `images/thumbs/volume12.jpg` を置く
3. HTMLを生成する
   ```
   python3 tools/build.py
   python3 tools/make_ogp.py      # 共有用画像（任意）
   ```
4. 変更したファイルをGitHubにアップロードする（`index.html`、`episodes/episode83.html`、`work.json` と追加した画像）

ページ数は画像の枚数から自動で数えます。`work.json` の `layout` は、話の番号（数字）はその話のページすべて、文字列は画像ファイル名（拡張子なし）を表します。`spread_from_cover` は、横向きの見開きを表紙から組むかどうかの設定です。

## 操作方法

- 縦向き: 左右スワイプ、または下の「次のページ／前のページ」ボタンでページをめくります。
- 横向き: 右から左の見開き表示です。PCは ← → キーでもめくれます。
- 途中まで読むと、次に開いたときに「続きから」と出ます（この端末のブラウザにだけ保存されます）。
