"""ModelIngest crawler 单元测试（离线，注入假 FETCH，不发真实网络请求）。"""

from __future__ import annotations

from pathlib import Path

import pytest

from modelingest import crawler
from modelingest.crawler import CrawlConfig, FetchResponse, crawl


@pytest.fixture(autouse=True)
def _reset_robots_cache():
    # robots 缓存是模块级全局，跨用例复用会串台，每个用例前清空。
    crawler._robots_cache.clear()
    yield
    crawler._robots_cache.clear()


def _fake_fetch(pages: dict[str, FetchResponse]):
    def fetch(url: str, headers: dict, timeout: float) -> FetchResponse:
        if url.endswith("/robots.txt"):
            return FetchResponse(status=404, body=b"", headers={})
        if url not in pages:
            return FetchResponse(status=404, body=b"not found", headers={})
        return pages[url]
    return fetch


def test_crawl_fetches_and_writes_file(tmp_path: Path, monkeypatch):
    url = "https://example.com/a.html"
    pages = {
        url: FetchResponse(status=200, body=b"<html>hello</html>",
                            headers={"content-type": "text/html", "etag": "v1"}),
    }
    monkeypatch.setattr(crawler, "FETCH", _fake_fetch(pages))

    out = tmp_path / "out"
    cfg = CrawlConfig(urls=[url], output_root=out, delay=0)
    summary = crawl(cfg)

    assert summary.fetched == 1
    assert summary.failed == 0
    written = out / "example.com" / "a.html"
    assert written.exists()
    assert written.read_bytes() == b"<html>hello</html>"


def test_crawl_incremental_skip_via_sha(tmp_path: Path, monkeypatch):
    url = "https://example.com/a.html"
    pages = {
        url: FetchResponse(status=200, body=b"same content",
                            headers={"content-type": "text/html"}),
    }
    monkeypatch.setattr(crawler, "FETCH", _fake_fetch(pages))

    out = tmp_path / "out"
    cfg = CrawlConfig(urls=[url], output_root=out, delay=0)

    first = crawl(cfg)
    assert first.fetched == 1

    second = crawl(cfg)
    assert second.fetched == 0
    assert second.skipped == 1


def test_crawl_reports_failed_on_http_error(tmp_path: Path, monkeypatch):
    url = "https://example.com/missing.html"
    monkeypatch.setattr(crawler, "FETCH", _fake_fetch({}))

    out = tmp_path / "out"
    cfg = CrawlConfig(urls=[url], output_root=out, delay=0)
    summary = crawl(cfg)

    assert summary.failed == 1
    assert summary.fetched == 0
    assert summary.results[0].status == "failed"


def test_crawl_follows_same_domain_links_within_depth(tmp_path: Path, monkeypatch):
    start = "https://example.com/index.html"
    linked = "https://example.com/page2.html"
    external = "https://other.com/page.html"
    pages = {
        start: FetchResponse(
            status=200,
            body=(
                b'<html><a href="/page2.html">p2</a>'
                b'<a href="https://other.com/page.html">ext</a></html>'
            ),
            headers={"content-type": "text/html"},
        ),
        linked: FetchResponse(status=200, body=b"<html>page2</html>", headers={"content-type": "text/html"}),
        external: FetchResponse(status=200, body=b"<html>external</html>", headers={"content-type": "text/html"}),
    }
    monkeypatch.setattr(crawler, "FETCH", _fake_fetch(pages))

    out = tmp_path / "out"
    cfg = CrawlConfig(urls=[start], output_root=out, max_depth=1, same_domain_only=True, delay=0)
    summary = crawl(cfg)

    fetched_urls = {r.url for r in summary.results if r.status == "fetched"}
    assert start in fetched_urls
    assert linked in fetched_urls
    assert external not in fetched_urls


def test_crawl_follows_unquoted_href_links(tmp_path: Path, monkeypatch):
    """回归测试：部分站点（如 oi-wiki.org，mkdocs-material 压缩输出）用不带引号的
    HTML5 属性写法（``href=dp/``），旧正则只认引号包裹的 href 会漏掉真实导航链接。"""
    start = "https://example.com/"
    linked = "https://example.com/dp/"
    pages = {
        start: FetchResponse(
            status=200,
            body=b'<html><a class=md-tabs__link href=dp/>dp</a></html>',
            headers={"content-type": "text/html"},
        ),
        linked: FetchResponse(status=200, body=b"<html>dp page</html>", headers={"content-type": "text/html"}),
    }
    monkeypatch.setattr(crawler, "FETCH", _fake_fetch(pages))

    out = tmp_path / "out"
    cfg = CrawlConfig(urls=[start], output_root=out, max_depth=1, same_domain_only=True, delay=0)
    summary = crawl(cfg)

    fetched_urls = {r.url for r in summary.results if r.status == "fetched"}
    assert start in fetched_urls
    assert linked in fetched_urls


def test_discover_collects_titles_without_writing_files(tmp_path: Path, monkeypatch):
    start = "https://example.com/index.html"
    linked = "https://example.com/page2.html"
    external = "https://other.com/page.html"
    pages = {
        start: crawler.FetchResponse(
            status=200,
            body=(
                b'<html><head><title>Home</title></head><body>'
                b'<a href="/page2.html">p2</a>'
                b'<a href="https://other.com/page.html">ext</a></body></html>'
            ),
            headers={"content-type": "text/html"},
        ),
        linked: crawler.FetchResponse(
            status=200,
            body=b"<html><head><title>Page 2</title></head></html>",
            headers={"content-type": "text/html"},
        ),
        external: crawler.FetchResponse(status=200, body=b"<html>external</html>", headers={"content-type": "text/html"}),
    }
    monkeypatch.setattr(crawler, "FETCH", _fake_fetch(pages))

    cfg = crawler.DiscoverConfig(urls=[start], max_depth=1, same_domain_only=True, delay=0)
    result = crawler.discover(cfg)

    assert result.total == 2
    assert result.ok == 2
    assert result.failed == 0
    titles = {e.url: e.title for e in result.entries}
    assert titles[start] == "Home"
    assert titles[linked] == "Page 2"
    depths = {e.url: e.depth for e in result.entries}
    assert depths[start] == 0
    assert depths[linked] == 1
    # 不落盘、不建 manifest：只是发现目录，不产生任何文件系统副作用。
    assert not (tmp_path / "example.com").exists()


def test_discover_reports_failed_urls(tmp_path: Path, monkeypatch):
    url = "https://example.com/missing.html"
    monkeypatch.setattr(crawler, "FETCH", _fake_fetch({}))

    cfg = crawler.DiscoverConfig(urls=[url], delay=0)
    result = crawler.discover(cfg)

    assert result.total == 1
    assert result.ok == 0
    assert result.failed == 1
    assert result.entries[0].status == "failed"


def test_crawl_respects_robots_disallow(tmp_path: Path, monkeypatch):
    url = "https://example.com/secret.html"
    robots_url = "https://example.com/robots.txt"

    def fetch(u: str, headers: dict, timeout: float) -> FetchResponse:
        if u == robots_url:
            return FetchResponse(status=200, body=b"User-agent: *\nDisallow: /secret.html\n", headers={})
        return FetchResponse(status=200, body=b"<html>secret</html>", headers={"content-type": "text/html"})

    monkeypatch.setattr(crawler, "FETCH", fetch)

    out = tmp_path / "out"
    cfg = CrawlConfig(urls=[url], output_root=out, respect_robots=True, delay=0)
    summary = crawl(cfg)

    assert summary.fetched == 0
    assert summary.failed == 1
    assert "robots" in summary.results[0].error
