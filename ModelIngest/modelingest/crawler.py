"""阶段 A 前置 —— 网页爬虫：抓取公开网页/文件到本地，供后续 parse 流程转换。

约定：
- 只做"抓取 + 落盘"，产物是原始文件（.html / .pdf / .txt ...），写入 ``--output``
  （通常指向某个 ``source_root`` 下的子目录）；随后用 ``modelingest run`` 按正常
  parse 流程转换成带溯源 front-matter 的 md，与本地文档一视同仁。
- 零运行时依赖：用标准库 ``urllib`` 请求，可通过全局可替换的 :data:`FETCH`
  注入测试替身（与 ``ModelProvider.http`` 的 ``TRANSPORT`` 同一套路）。
- 礼貌抓取：默认遵守 robots.txt，请求间加 ``delay`` 秒间隔，可关闭。
- 增量：sqlite manifest 按 URL 记录 etag / last-modified / sha256；未变则跳过
  （优先用条件请求 If-None-Match / If-Modified-Since，退化时用内容 sha256 兜底）。
- 可选浅层深度抓取：``max_depth=0`` 只抓给定 URL；>0 时从 HTML 中提取 ``<a href>``
  链接继续抓取（默认限制同域，且有 ``max_pages`` 安全上限防止失控）。
"""

from __future__ import annotations

import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Callable, Optional

DEFAULT_USER_AGENT = "ModelIngest-Crawler/0.1 (+ModelToolbox; respectful, low-rate public-data fetcher)"

# 常见 content-type → 落盘扩展名（未命中则退回 URL 路径自带后缀，再退回 .html）。
_CONTENT_TYPE_EXT = {
    "text/html": ".html",
    "application/xhtml+xml": ".html",
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/csv": ".csv",
}

_LINK_RE = re.compile(r'href=["\']([^"\'#]+)', re.IGNORECASE)


class CrawlError(RuntimeError):
    """单个 URL 抓取失败（网络错误；4xx/5xx 由调用方按状态码处理，不在此抛出）。"""


@dataclass
class FetchResponse:
    status: int
    body: bytes
    headers: dict  # 小写 key


# 可替换的抓取函数：(url, headers, timeout) -> FetchResponse。测试里可整体替换。
FetchFn = Callable[[str, dict, float], FetchResponse]


def _urllib_fetch(url: str, headers: dict, timeout: float) -> FetchResponse:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            hdrs = {k.lower(): v for k, v in resp.headers.items()}
            return FetchResponse(status=resp.getcode(), body=body, headers=hdrs)
    except urllib.error.HTTPError as e:
        # 304 / 4xx / 5xx：仍返回响应体供调用方按状态码分支处理。
        body = e.read() if e.fp else b""
        hdrs = {k.lower(): v for k, v in (e.headers.items() if e.headers else [])}
        return FetchResponse(status=e.code, body=body, headers=hdrs)
    except urllib.error.URLError as e:
        raise CrawlError(f"无法连接 {url}: {e.reason}") from e


# 全局可替换的抓取实现（默认标准库 urllib），测试用 monkeypatch 换成假实现。
FETCH: FetchFn = _urllib_fetch


@dataclass
class CrawlConfig:
    """一次抓取运行的配置。"""

    urls: list[str]
    output_root: Path
    manifest_path: Path = field(default=Path(".crawl_cache/crawl_manifest.sqlite"))
    max_depth: int = 0  # 0 = 只抓给定 URL，不跟随链接
    same_domain_only: bool = True
    delay: float = 1.0  # 请求间隔秒数（礼貌抓取）
    timeout: float = 20.0
    user_agent: str = DEFAULT_USER_AGENT
    respect_robots: bool = True
    overwrite: bool = False  # True 时忽略 manifest，强制重新抓取
    max_pages: int = 200  # 安全上限，防止深度抓取失控

    def __post_init__(self) -> None:
        self.output_root = Path(self.output_root).resolve()
        self.manifest_path = Path(self.manifest_path)
        if not self.manifest_path.is_absolute():
            self.manifest_path = (self.output_root / self.manifest_path).resolve()


@dataclass
class CrawlResult:
    url: str
    status: str  # "fetched" | "skipped" | "failed"
    local_path: str | None = None
    error: str | None = None


@dataclass
class CrawlSummary:
    fetched: int = 0
    skipped: int = 0
    failed: int = 0
    results: list[CrawlResult] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# 增量 manifest：按 URL 记录 etag / last-modified / sha256。
# --------------------------------------------------------------------------- #

_SCHEMA = """
CREATE TABLE IF NOT EXISTS crawled (
    url           TEXT PRIMARY KEY,
    sha256        TEXT NOT NULL,
    etag          TEXT,
    last_modified TEXT,
    local_path    TEXT NOT NULL,
    fetched_at    TEXT NOT NULL
);
"""


class CrawlManifest:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        with closing(self._conn.cursor()) as cur:
            cur.executescript(_SCHEMA)
        self._conn.commit()

    def get(self, url: str) -> Optional[tuple]:
        """返回 (sha256, etag, last_modified, local_path) 或 None。"""
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "SELECT sha256, etag, last_modified, local_path FROM crawled WHERE url = ?",
                (url,),
            )
            return cur.fetchone()

    def record(
        self,
        url: str,
        sha256_hex: str,
        etag: str | None,
        last_modified: str | None,
        local_path: str,
    ) -> None:
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "INSERT OR REPLACE INTO crawled "
                "(url, sha256, etag, last_modified, local_path, fetched_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (url, sha256_hex, etag, last_modified, local_path,
                 datetime.now(timezone.utc).isoformat()),
            )
        self._conn.commit()

    def all_records(self) -> list[tuple]:
        with closing(self._conn.cursor()) as cur:
            cur.execute("SELECT url, sha256, etag, last_modified, local_path, fetched_at FROM crawled")
            return cur.fetchall()

    def close(self) -> None:
        self._conn.close()


# --------------------------------------------------------------------------- #
# robots.txt
# --------------------------------------------------------------------------- #

_robots_cache: dict[str, Optional[urllib.robotparser.RobotFileParser]] = {}


def _get_robots(base_url: str, user_agent: str, timeout: float) -> Optional[urllib.robotparser.RobotFileParser]:
    if base_url in _robots_cache:
        return _robots_cache[base_url]
    rp: Optional[urllib.robotparser.RobotFileParser] = None
    try:
        resp = FETCH(f"{base_url}/robots.txt", {"User-Agent": user_agent}, timeout)
        if resp.status == 200:
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(resp.body.decode("utf-8", "replace").splitlines())
    except CrawlError:
        rp = None
    _robots_cache[base_url] = rp
    return rp


def _robots_allowed(url: str, user_agent: str, timeout: float) -> bool:
    parsed = urllib.parse.urlsplit(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    rp = _get_robots(base, user_agent, timeout)
    if rp is None:
        return True  # 没有 robots.txt 或无法获取 → 默认允许
    return rp.can_fetch(user_agent, url)


# --------------------------------------------------------------------------- #
# URL → 本地文件名
# --------------------------------------------------------------------------- #

_UNSAFE = re.compile(r"[^\w./-]+")


def _slug_for_url(url: str) -> str:
    """URL → 落盘相对路径（不含扩展名，由调用方按 content-type 追加）。"""
    parsed = urllib.parse.urlsplit(url)
    host = parsed.netloc.replace(":", "_")
    raw_path = parsed.path.strip("/") or "index"
    # 去掉 URL 路径自带的扩展名，避免和最终按 content-type 追加的扩展名重复
    # （如 "/a.html" 不应变成 "a.html.html"）。
    stem = PurePosixPath(raw_path)
    path = str(stem.with_suffix("")) if stem.suffix else str(stem)
    path = _UNSAFE.sub("_", path)
    if parsed.query:
        path = f"{path}__{_UNSAFE.sub('_', parsed.query)}"
    return f"{host}/{path}"


def _ext_for(content_type: str, url: str) -> str:
    ctype = content_type.split(";")[0].strip().lower()
    if ctype in _CONTENT_TYPE_EXT:
        return _CONTENT_TYPE_EXT[ctype]
    suffix = Path(urllib.parse.urlsplit(url).path).suffix
    return suffix if suffix else ".html"


def _extract_links(html: str, base_url: str, same_domain_only: bool) -> list[str]:
    base_parsed = urllib.parse.urlsplit(base_url)
    out: list[str] = []
    for m in _LINK_RE.finditer(html):
        abs_url = urllib.parse.urljoin(base_url, m.group(1))
        parsed = urllib.parse.urlsplit(abs_url)
        if parsed.scheme not in ("http", "https"):
            continue
        if same_domain_only and parsed.netloc != base_parsed.netloc:
            continue
        out.append(urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, "")))
    return out


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #

def crawl(cfg: CrawlConfig) -> CrawlSummary:
    """抓取 ``cfg.urls``（及可选跟随链接），落盘到 ``cfg.output_root``。"""
    cfg.output_root.mkdir(parents=True, exist_ok=True)
    manifest = CrawlManifest(cfg.manifest_path)
    summary = CrawlSummary()
    seen: set[str] = set()
    queue: list[tuple[str, int]] = [(u, 0) for u in cfg.urls]

    try:
        while queue and len(seen) < cfg.max_pages:
            url, depth = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)

            if cfg.respect_robots and not _robots_allowed(url, cfg.user_agent, cfg.timeout):
                summary.failed += 1
                summary.results.append(CrawlResult(url, "failed", error="disallowed by robots.txt"))
                continue

            prior = manifest.get(url)
            headers = {"User-Agent": cfg.user_agent}
            if prior and not cfg.overwrite:
                if prior[1]:
                    headers["If-None-Match"] = prior[1]
                if prior[2]:
                    headers["If-Modified-Since"] = prior[2]

            try:
                resp = FETCH(url, headers, cfg.timeout)
            except CrawlError as exc:
                summary.failed += 1
                summary.results.append(CrawlResult(url, "failed", error=str(exc)))
                continue

            if resp.status == 304:
                summary.skipped += 1
                summary.results.append(CrawlResult(url, "skipped", local_path=prior[3] if prior else None))
                continue

            if resp.status >= 400:
                summary.failed += 1
                summary.results.append(CrawlResult(url, "failed", error=f"HTTP {resp.status}"))
                continue

            digest = sha256(resp.body).hexdigest()
            if prior and not cfg.overwrite and prior[0] == digest:
                summary.skipped += 1
                summary.results.append(CrawlResult(url, "skipped", local_path=prior[3]))
                continue

            ext = _ext_for(resp.headers.get("content-type", ""), url)
            rel_path = f"{_slug_for_url(url)}{ext}"
            out_path = cfg.output_root / rel_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(resp.body)

            manifest.record(
                url=url,
                sha256_hex=digest,
                etag=resp.headers.get("etag"),
                last_modified=resp.headers.get("last-modified"),
                local_path=rel_path,
            )
            summary.fetched += 1
            summary.results.append(CrawlResult(url, "fetched", local_path=rel_path))

            if depth < cfg.max_depth and ext == ".html":
                for link in _extract_links(resp.body.decode("utf-8", "replace"), url, cfg.same_domain_only):
                    if link not in seen:
                        queue.append((link, depth + 1))

            if cfg.delay > 0 and queue:
                time.sleep(cfg.delay)
    finally:
        manifest.close()

    return summary
