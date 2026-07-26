from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

import typer

from modeltoolbox_core.jsonio import dump_json

from modelingest import pipeline
from modelingest.config import IngestConfig
from modelingest.crawler import CrawlConfig, DEFAULT_USER_AGENT, DiscoverConfig, crawl as crawl_run, discover as discover_run
from modelingest.organizer import OrganizeConfig, organize_knowledge_base

app = typer.Typer(help="Build structured Markdown libraries from web and local sources.")


def register(root: typer.Typer) -> None:
    root.add_typer(app, name="ingest")


@app.command()
def doctor() -> None:
    typer.echo("ingest: registered")


def _source_config(
    source: Path,
    output: Path,
    manifest: Path,
    overwrite: bool = False,
    include: list[str] | None = None,
    extract_pdf_pages: bool = True,
    clean_html: bool = True,
    neutralize_injection: bool = True,
    quality_filter: bool = True,
    near_dup_check: bool = True,
) -> IngestConfig:
    return IngestConfig(
        source_root=source,
        output_root=output,
        manifest_path=manifest,
        overwrite=overwrite,
        include=set(include) if include else None,
        extract_pdf_pages=extract_pdf_pages,
        clean_html=clean_html,
        neutralize_injection=neutralize_injection,
        quality_filter=quality_filter,
        near_dup_check=near_dup_check,
    )


def _collect_urls(url: list[str], urls_file: Path | None) -> list[str]:
    urls = list(url)
    if urls_file:
        text = urls_file.read_text(encoding="utf-8")
        urls.extend(line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))
    return urls


@app.command()
def discover(
    url: list[str] = typer.Option(None, "--url", "-u", help="Seed URL. Can be passed more than once."),
    urls_file: Path | None = typer.Option(None, help="Text file with one URL per line."),
    depth: int = typer.Option(1, min=0, help="Link discovery depth."),
    allow_cross_domain: bool = typer.Option(False, help="Allow following links outside the seed domain."),
    delay: float = typer.Option(0.5, min=0, help="Delay between requests in seconds."),
    timeout: float = typer.Option(20.0, min=1, help="Request timeout in seconds."),
    max_pages: int = typer.Option(100, min=1, help="Maximum pages to discover."),
    ignore_robots: bool = typer.Option(False, help="Ignore robots.txt."),
    user_agent: str | None = typer.Option(None, help="Custom User-Agent."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    urls = _collect_urls(url or [], urls_file)
    if not urls:
        typer.echo("Provide at least one --url or --urls-file.", err=True)
        raise typer.Exit(2)
    result = discover_run(
        DiscoverConfig(
            urls=urls,
            max_depth=depth,
            same_domain_only=not allow_cross_domain,
            delay=delay,
            timeout=timeout,
            user_agent=user_agent or DEFAULT_USER_AGENT,
            respect_robots=not ignore_robots,
            max_pages=max_pages,
        )
    )
    payload = {"total": result.total, "ok": result.ok, "failed": result.failed, "entries": [asdict(item) for item in result.entries]}
    if json_output:
        dump_json(payload)
        return
    typer.echo(f"discovered {result.total} pages, ok={result.ok}, failed={result.failed}")


@app.command()
def crawl(
    url: list[str] = typer.Option(None, "--url", "-u", help="URL to fetch. Can be passed more than once."),
    output: Path = typer.Option(..., "--output", "-o", help="Raw crawl output directory."),
    urls_file: Path | None = typer.Option(None, help="Text file with one URL per line."),
    manifest: Path = typer.Option(Path(".crawl_cache/crawl_manifest.sqlite"), help="Crawl manifest path."),
    depth: int = typer.Option(0, min=0, help="Follow-link depth."),
    allow_cross_domain: bool = typer.Option(False, help="Allow following links outside the seed domain."),
    delay: float = typer.Option(1.0, min=0, help="Delay between requests in seconds."),
    timeout: float = typer.Option(20.0, min=1, help="Request timeout in seconds."),
    max_pages: int = typer.Option(200, min=1, help="Maximum pages to fetch."),
    ignore_robots: bool = typer.Option(False, help="Ignore robots.txt."),
    overwrite: bool = typer.Option(False, help="Ignore manifest and refetch."),
    user_agent: str | None = typer.Option(None, help="Custom User-Agent."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    urls = _collect_urls(url or [], urls_file)
    if not urls:
        typer.echo("Provide at least one --url or --urls-file.", err=True)
        raise typer.Exit(2)
    summary = crawl_run(
        CrawlConfig(
            urls=urls,
            output_root=output,
            manifest_path=manifest,
            max_depth=depth,
            same_domain_only=not allow_cross_domain,
            delay=delay,
            timeout=timeout,
            user_agent=user_agent or DEFAULT_USER_AGENT,
            respect_robots=not ignore_robots,
            overwrite=overwrite,
            max_pages=max_pages,
        )
    )
    payload = {"fetched": summary.fetched, "skipped": summary.skipped, "failed": summary.failed, "results": [asdict(item) for item in summary.results]}
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"fetched={summary.fetched} skipped={summary.skipped} failed={summary.failed}")
    if summary.failed and not summary.fetched:
        raise typer.Exit(1)


@app.command()
def scan(
    source: Path = typer.Option(..., "--source", "-s", help="Raw document source directory."),
    output: Path = typer.Option(..., "--output", "-o", help="Markdown output directory."),
    manifest: Path = typer.Option(Path(".ingest_cache/ingest_manifest.sqlite"), help="Ingest manifest path."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    entries = pipeline.scan(_source_config(source, output, manifest))
    payload = {"files": [asdict(item) for item in entries]}
    if json_output:
        dump_json(payload)
    else:
        for item in entries:
            typer.echo(f"{item.status}\t{item.rel_path}")


@app.command()
def run(
    source: Path = typer.Option(..., "--source", "-s", help="Raw document source directory."),
    output: Path = typer.Option(..., "--output", "-o", help="Markdown output directory."),
    manifest: Path = typer.Option(Path(".ingest_cache/ingest_manifest.sqlite"), help="Ingest manifest path."),
    include: list[str] | None = typer.Option(None, help="Relative path to convert. Can be passed more than once."),
    overwrite: bool = typer.Option(False, help="Ignore manifest and reconvert."),
    no_pdf_pages: bool = typer.Option(False, help="Disable PDF page image extraction."),
    no_html_clean: bool = typer.Option(False, help="Disable HTML boilerplate cleanup."),
    no_injection_scan: bool = typer.Option(False, help="Disable prompt-injection neutralization."),
    no_quality_filter: bool = typer.Option(False, help="Disable low-quality source filtering."),
    no_dedup: bool = typer.Option(False, help="Disable near-duplicate checks."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    summary = pipeline.run(
        _source_config(
            source,
            output,
            manifest,
            overwrite=overwrite,
            include=include,
            extract_pdf_pages=not no_pdf_pages,
            clean_html=not no_html_clean,
            neutralize_injection=not no_injection_scan,
            quality_filter=not no_quality_filter,
            near_dup_check=not no_dedup,
        )
    )
    payload = {"converted": summary.converted, "skipped": summary.skipped, "filtered": summary.filtered, "failed": summary.failed, "results": [asdict(item) for item in summary.results]}
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"converted={summary.converted} skipped={summary.skipped} filtered={summary.filtered} failed={summary.failed}")
    if summary.failed:
        raise typer.Exit(1)


@app.command()
def status(
    source: Path = typer.Option(..., "--source", "-s", help="Raw document source directory."),
    output: Path = typer.Option(..., "--output", "-o", help="Markdown output directory."),
    manifest: Path = typer.Option(Path(".ingest_cache/ingest_manifest.sqlite"), help="Ingest manifest path."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    payload = pipeline.status(_source_config(source, output, manifest))
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"recorded={payload['recorded']} pending_new={payload['pending_new']} pending_changed={payload['pending_changed']} stale={payload['stale_source_deleted']}")


@app.command()
def clean(
    source: Path = typer.Option(..., "--source", "-s", help="Raw document source directory."),
    output: Path = typer.Option(..., "--output", "-o", help="Markdown output directory."),
    manifest: Path = typer.Option(Path(".ingest_cache/ingest_manifest.sqlite"), help="Ingest manifest path."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    removed = pipeline.clean(_source_config(source, output, manifest))
    if json_output:
        dump_json({"removed": removed})
    else:
        typer.echo(f"removed={removed}")


@app.command()
def build(
    source: Path = typer.Option(..., "--source", "-s", help="Local raw document directory."),
    output: Path = typer.Option(..., "--output", "-o", help="Structured Markdown library output directory."),
    domain: str = typer.Option("通用", help="Knowledge domain used for MOC grouping."),
    structure: str = typer.Option("obsidian", help="Output structure: obsidian, flat, or hierarchical."),
    overwrite: bool = typer.Option(False, help="Ignore manifest and reconvert."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    with TemporaryDirectory(prefix="mtb-ingest-") as temp_dir:
        parsed_dir = Path(temp_dir) / "parsed"
        parse_summary = pipeline.run(_source_config(source, parsed_dir, Path(".ingest_cache/ingest_manifest.sqlite"), overwrite=overwrite))
        organize_stats = organize_knowledge_base(
            OrganizeConfig(source_dir=parsed_dir, output_dir=output, structure=structure, domain=domain)
        )
    payload = {
        "converted": parse_summary.converted,
        "skipped": parse_summary.skipped,
        "filtered": parse_summary.filtered,
        "failed": parse_summary.failed,
        "organized": organize_stats,
    }
    if json_output:
        dump_json(payload)
    else:
        typer.echo(f"converted={parse_summary.converted} skipped={parse_summary.skipped} filtered={parse_summary.filtered} failed={parse_summary.failed}")
        typer.echo(f"organized={organize_stats['total_notes']} notes")
    if parse_summary.failed:
        raise typer.Exit(1)
