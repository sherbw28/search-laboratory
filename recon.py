#!/usr/bin/env python3
"""偵察用スクリプト: robots.txt を確認し、対象ページを 1 回だけ取得して構造を報告する。

使い方:
    python3 recon.py <URL>

出力:
  - robots.txt の取得結果と、該当パスがこの User-Agent で許可されているか
  - ページを 1 回取得して: HTTP ステータス、Content-Type、タイトル、
    リンク数、<table> の有無、<form> の有無、PDF リンクの有無（最大5件表示）、
    CSV/API らしきリンクの有無（最大5件表示）

収集はしない。取得は robots.txt + 対象ページの計 2 リクエストのみで、
間に 2 秒の待機を入れる。robots.txt で不許可ならページ取得は行わない。
"""
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

USER_AGENT = (
    "search-laboratory-recon/0.1 (+contact: eisukedayodayo@gmail.com)"
)
TIMEOUT = 30
WAIT_SECONDS = 2


class PageInspector(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.title = ""
        self._in_title = False
        self.links: list[str] = []
        self.table_count = 0
        self.form_count = 0
        self.frame_srcs: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "a" and attrs.get("href"):
            self.links.append(urljoin(self.base_url, attrs["href"]))
        elif tag == "table":
            self.table_count += 1
        elif tag == "form":
            self.form_count += 1
        elif tag in ("frame", "iframe") and attrs.get("src"):
            self.frame_srcs.append(urljoin(self.base_url, attrs["src"]))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def check_robots(url: str) -> tuple[bool, str]:
    """robots.txt を確認し、(許可されているか, 説明) を返す。"""
    parts = urlsplit(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    req = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return False, f"robots.txt: HTTP {e.code}（全アクセス不許可とみなす）"
        return True, f"robots.txt: HTTP {e.code}（robots.txt なし → 許可とみなす）"
    except Exception as e:
        return False, f"robots.txt: 取得失敗 ({e})（安全側に倒して不許可扱い）"

    rp.parse(body.splitlines())
    allowed = rp.can_fetch(USER_AGENT, url)
    lines = len(body.splitlines())
    return allowed, (
        f"robots.txt: 取得成功 ({robots_url}, {lines} 行)\n"
        f"  このパスは {'許可' if allowed else '不許可'}: {url}"
    )


def fetch_once(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read()
        return resp.status, resp.headers.get("Content-Type", ""), resp.geturl(), body


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    url = sys.argv[1]

    allowed, msg = check_robots(url)
    print(msg)
    if not allowed:
        print("robots.txt で不許可のため、ページ取得は行いません。")
        sys.exit(2)

    time.sleep(WAIT_SECONDS)

    try:
        status, ctype, final_url, body = fetch_once(url)
    except Exception as e:
        print(f"ページ取得失敗: {e}")
        sys.exit(3)

    print(f"\nHTTP {status}  Content-Type: {ctype}")
    if final_url != url:
        print(f"リダイレクト先: {final_url}")
    print(f"サイズ: {len(body):,} bytes")

    if "html" not in ctype.lower():
        print("HTML ではないため構造解析はスキップします。")
        return

    # charset は Content-Type から推定し、失敗時は UTF-8 で読む
    charset = "utf-8"
    if "charset=" in ctype.lower():
        charset = ctype.lower().split("charset=")[-1].split(";")[0].strip()
    text = body.decode(charset, errors="replace")

    insp = PageInspector(final_url)
    insp.feed(text)

    pdf_links = [l for l in insp.links if urlsplit(l).path.lower().endswith(".pdf")]
    data_links = [
        l
        for l in insp.links
        if any(k in l.lower() for k in (".csv", ".json", ".xlsx", "api", "download", "export"))
    ]

    print(f"\nタイトル: {insp.title.strip() or '(なし)'}")
    print(f"リンク数: {len(insp.links)}")
    print(f"<table>: {insp.table_count} 個")
    print(f"<form>:  {insp.form_count} 個")
    if insp.frame_srcs:
        print(f"frame/iframe: {len(insp.frame_srcs)} 個")
        for s in insp.frame_srcs[:5]:
            print(f"  - {s}")
    print(f"PDF リンク: {len(pdf_links)} 件")
    for l in pdf_links[:5]:
        print(f"  - {l}")
    print(f"CSV/API らしきリンク: {len(data_links)} 件")
    for l in data_links[:5]:
        print(f"  - {l}")


if __name__ == "__main__":
    main()
