# 偵察メモ: 筑波大学 KdB（情報学群シラバス）

調査日: 2026-10-17

## 結論

- **kdb.tsukuba.ac.jp への自動アクセスは不可**（robots.txt が `User-agent: * / Disallow: /`）。
- 科目一覧＋授業概要＋担当教員は、KdB の公式機能「科目一覧ダウンロード」（CSV, CP932）を**人手でブラウザから取得**するのが第一候補。
- 大学公式サイト（www.tsukuba.ac.jp）には学類ごとの開設授業科目一覧 PDF があり、robots.txt 上は取得可。ただし PDF で、2026-02-13 時点のスナップショット。

## 調べたもの

| URL | robots | 結果 |
|---|---|---|
| https://kdb.tsukuba.ac.jp/ | 不許可（全面 Disallow） | 取得せず |
| https://www.tsukuba.ac.jp/education/ug-courses-openclass/ | 許可 | HTML 210KB、`学群 開設授業科目一覧（2026年度）`。学群ごとの見出し＋学類ごとの PDF リンク。本文中に表はなし（table 2 個はサイト枠組み） |
| https://www.tsukuba.ac.jp/education/ug-courses-openclass/2026/pdf/inf-information-science.pdf | 許可 | PDF 287KB（情報科学類） |

情報学群の PDF（同ディレクトリ `2026/pdf/`）:
`inf-common-subjects.pdf`（学群共通）, `inf-information-science.pdf`（情報科学類）,
`inf-media-arts.pdf`（情報メディア創成学類）, `inf-library-sciences.pdf`（知識情報・図書館学類）,
`full-version.pdf`（全学群一括）。

## KdB の公式ダウンロード機能（マニュアルより）

- 検索後「科目一覧ダウンロード」→ `kdb_yyyymmddhhmmss.csv`（Shift_JIS/CP932）または Excel。
- 「シラバスダウンロード」→ 検索結果全科目のシラバス PDF 一括。
- ログイン不要（公開システム）。英語表示切替あり。
- CSV 列（第三者ツールのスキーマから推定、要実物確認）: 科目番号, 科目名, 授業方法, 単位数, 標準履修年次, 実施学期, 曜時限, 教室, 担当教員, 授業概要, 備考, データ更新日 など。

## 第三者の公開データ（参考・一次ソースにはしない）

- Make-IT-TSUKUBA/alternative-tsukuba-kdb（MPL-2.0, 情報メディア創成学類公認の非公式サイト）: `/csv/kdb-YYYYMMDD.csv` を GitHub Actions で定期更新。取得は `tools/python/download.py` が KdB に直接 POST（`pageId=SB0070, action=downloadList, cmbDwldtype=csv, hdnFy=年度`）。robots.txt 無視・UA 未設定・待機なしのため**本プロジェクトでは同じ方法を採らない**。
- s7tya/kdb-crawler: 同様に自動取得し `dist/kdb.json` を公開。

## 利用条件

- KdB 自体の利用規約ページは見つからず。
- www.tsukuba.ac.jp サイトポリシー（/sitepolicy/）: 記事・写真等は著作権法で保護、無断複製・転載を禁止。リンクは原則自由。データベース化・二次利用への明示的言及なし。
- → 本格収集前に大学（/contact/）へ利用目的を伝えて確認するのが安全。

## 次のステップ案

1. 人手で KdB から情報学群（情報科学類・情報メディア創成学類・知識情報・図書館学類）の CSV を取得し `data/raw/tsukuba/` に保存（取得日時・URL をファイル名/メモに残す）。
2. CSV 取り込みスクリプトを書く（CP932 → UTF-8、`source_url=https://kdb.tsukuba.ac.jp/`, `fetched_at=手動取得日時`）。
3. 公式 PDF は列構成の突合・欠損補完用の副次ソースとして扱う。
