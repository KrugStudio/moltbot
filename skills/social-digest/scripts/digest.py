#!/usr/bin/env python3
"""Pull captions, transcripts, and images for a batch of social links into one digest.

Usage:
  digest.py URL [URL ...] [--file links.txt] [--out DIR]
            [--cookies-from-browser chrome] [--no-transcribe] [--no-images]
            [--whisper-model small]

Writes DIR/digest.md (one section per link) plus DIR/NN-<slug>/ folders holding
info.json, caption.txt, transcript.txt, and images/. Stdlib only; shells out to
yt-dlp (required for social links), whisper + ffmpeg (transcripts), gallery-dl
(carousel images), and summarize (non-social pages) when they are installed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SOCIAL_HOSTS = (
    "instagram.com",
    "tiktok.com",
    "youtube.com",
    "youtu.be",
    "x.com",
    "twitter.com",
    "threads.net",
    "facebook.com",
    "linkedin.com",
)
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
AUDIO_EXTS = {".m4a", ".mp3", ".mp4", ".webm", ".opus", ".aac", ".wav"}


def have(binary: str) -> bool:
    return shutil.which(binary) is not None


def run(cmd: list[str], timeout: int = 600) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 124, "", f"timed out after {timeout}s")


def clean_url(url: str) -> str:
    """Drop share-tracking query params (igsh, stkn, vrfl, ...) that can trip extractors."""
    parts = urllib.parse.urlsplit(url.strip())
    host = parts.netloc.lower()
    if any(host.endswith(h) for h in SOCIAL_HOSTS) and "youtube.com" not in host:
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    return url.strip()


def is_social(url: str) -> bool:
    host = urllib.parse.urlsplit(url).netloc.lower()
    return any(host == h or host.endswith("." + h) for h in SOCIAL_HOSTS)


def slug_for(url: str) -> str:
    path = [p for p in urllib.parse.urlsplit(url).path.split("/") if p]
    base = path[-1] if path else urllib.parse.urlsplit(url).netloc
    return re.sub(r"[^A-Za-z0-9_-]+", "-", base)[:60] or "link"


def cookie_args(browser: str | None) -> list[str]:
    return ["--cookies-from-browser", browser] if browser else []


def fetch_social(url: str, item_dir: Path, args: argparse.Namespace) -> dict:
    result: dict = {"kind": "social", "notes": []}
    if not have("yt-dlp"):
        result["notes"].append("yt-dlp not installed: brew install yt-dlp")
        return result

    meta = run(
        ["yt-dlp", "-J", "--ignore-no-formats-error", "--no-warnings"]
        + cookie_args(args.cookies_from_browser)
        + [url],
        timeout=180,
    )
    if meta.returncode != 0 or not meta.stdout.strip():
        err = (meta.stderr or "").strip().splitlines()
        result["notes"].append("metadata failed: " + (err[-1] if err else "unknown error"))
        if "login" in (meta.stderr or "").lower() and not args.cookies_from_browser:
            result["notes"].append("retry with --cookies-from-browser chrome")
    else:
        info = json.loads(meta.stdout)
        (item_dir / "info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        entries = info.get("entries") or []
        first = entries[0] if entries and isinstance(entries[0], dict) else {}
        result.update(
            title=info.get("title") or first.get("title"),
            author=info.get("uploader") or info.get("channel") or first.get("uploader"),
            date=info.get("upload_date") or first.get("upload_date"),
            likes=info.get("like_count") or first.get("like_count"),
            comments=info.get("comment_count") or first.get("comment_count"),
            duration=info.get("duration") or first.get("duration"),
            caption=(info.get("description") or first.get("description") or "").strip(),
            media_count=len(entries) if entries else 1,
        )
        has_video = any(
            (e or {}).get("duration") or (e or {}).get("vcodec") not in (None, "none")
            for e in (entries or [info])
        )
        result["has_video"] = bool(has_video)
        if result["caption"]:
            (item_dir / "caption.txt").write_text(result["caption"] + "\n", encoding="utf-8")

    if args.transcribe and result.get("has_video"):
        transcribe(url, item_dir, args, result)

    if args.images and have("gallery-dl"):
        img_dir = item_dir / "images"
        gl = run(
            ["gallery-dl", "-D", str(img_dir)] + cookie_args(args.cookies_from_browser) + [url],
            timeout=300,
        )
        if gl.returncode != 0:
            result["notes"].append("gallery-dl failed (images not saved)")
    elif args.images:
        result["notes"].append("gallery-dl not installed: carousel images skipped (brew install gallery-dl)")

    images = sorted(p for p in item_dir.rglob("*") if p.suffix.lower() in IMAGE_EXTS)
    result["images"] = [str(p.relative_to(item_dir)) for p in images]
    return result


def transcribe(url: str, item_dir: Path, args: argparse.Namespace, result: dict) -> None:
    if not (have("whisper") and have("ffmpeg")):
        result["notes"].append("transcript skipped: needs whisper + ffmpeg (brew install openai-whisper ffmpeg)")
        return
    audio_dir = item_dir / "audio"
    dl = run(
        ["yt-dlp", "-f", "ba/b", "-x", "--audio-format", "m4a", "--no-warnings",
         "-o", str(audio_dir / "%(playlist_index|1)s.%(ext)s")]
        + cookie_args(args.cookies_from_browser)
        + [url],
        timeout=600,
    )
    files = sorted(p for p in audio_dir.glob("*") if p.suffix.lower() in AUDIO_EXTS)
    if dl.returncode != 0 or not files:
        result["notes"].append("audio download failed (no transcript)")
        return
    texts = []
    for audio in files:
        wh = run(
            ["whisper", str(audio), "--model", args.whisper_model,
             "--output_format", "txt", "--output_dir", str(audio_dir)],
            timeout=1800,
        )
        txt = audio.with_suffix(".txt")
        if wh.returncode == 0 and txt.exists():
            texts.append(txt.read_text(encoding="utf-8").strip())
        else:
            result["notes"].append(f"whisper failed on {audio.name}")
    if texts:
        transcript = "\n\n".join(texts)
        (item_dir / "transcript.txt").write_text(transcript + "\n", encoding="utf-8")
        result["transcript"] = transcript


def fetch_page(url: str, item_dir: Path) -> dict:
    result: dict = {"kind": "page", "notes": []}
    text = ""
    if have("summarize"):
        sm = run(["summarize", url, "--extract-only"], timeout=180)
        if sm.returncode == 0:
            text = sm.stdout.strip()
        else:
            result["notes"].append("summarize --extract-only failed; used plain fetch")
    if not text:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            title = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
            result["title"] = html.unescape(title.group(1).strip()) if title else None
            body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
            text = html.unescape(re.sub(r"<[^>]+>", " ", body))
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) < 200:
                result["notes"].append("page is mostly JavaScript (e.g. Notion): open it in a browser or install summarize")
        except Exception as exc:  # network errors vary widely by platform
            result["notes"].append(f"fetch failed: {exc}")
    if text:
        (item_dir / "page.txt").write_text(text + "\n", encoding="utf-8")
        result["caption"] = text
    return result


def render_section(index: int, url: str, item_dir: Path, r: dict) -> str:
    lines = [f"## {index:02d}. {r.get('title') or slug_for(url)}", "", f"- URL: {url}"]
    for key, label in (("author", "Author"), ("date", "Date"), ("likes", "Likes"),
                       ("comments", "Comments"), ("duration", "Duration (s)"),
                       ("media_count", "Media items")):
        if r.get(key) not in (None, ""):
            lines.append(f"- {label}: {r[key]}")
    lines.append(f"- Folder: {item_dir.name}/")
    if r.get("images"):
        lines.append(f"- Images ({len(r['images'])}): " + ", ".join(r["images"][:12]))
    for note in r.get("notes", []):
        lines.append(f"- NOTE: {note}")
    if r.get("caption"):
        label = "Page text" if r["kind"] == "page" else "Caption"
        body = r["caption"] if len(r["caption"]) <= 4000 else r["caption"][:4000] + " …(truncated, see folder)"
        lines += ["", f"### {label}", "", body]
    if r.get("transcript"):
        body = r["transcript"] if len(r["transcript"]) <= 6000 else r["transcript"][:6000] + " …(truncated, see transcript.txt)"
        lines += ["", "### Transcript", "", body]
    if not r.get("caption") and not r.get("transcript"):
        lines += ["", "_No text captured. Check the notes above, or paste screenshots._"]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--file", help="text file with one URL per line (# comments allowed)")
    ap.add_argument("--out", help="output directory (default: ./social-digest-YYYYMMDD-HHMM)")
    ap.add_argument("--cookies-from-browser", help="e.g. chrome, safari, brave, firefox (for login-walled posts)")
    ap.add_argument("--no-transcribe", dest="transcribe", action="store_false")
    ap.add_argument("--no-images", dest="images", action="store_false")
    ap.add_argument("--whisper-model", default="small")
    args = ap.parse_args()

    urls = list(args.urls)
    if args.file:
        for line in Path(args.file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    urls = [u for u in (clean_url(u) for u in urls) if u.startswith("http")]
    if not urls:
        ap.error("no URLs given")

    out = Path(args.out or f"social-digest-{dt.datetime.now():%Y%m%d-%H%M}").expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    sections = []
    for i, url in enumerate(urls, 1):
        item_dir = out / f"{i:02d}-{slug_for(url)}"
        item_dir.mkdir(exist_ok=True)
        print(f"[{i}/{len(urls)}] {url}", file=sys.stderr)
        r = fetch_social(url, item_dir, args) if is_social(url) else fetch_page(url, item_dir)
        sections.append(render_section(i, url, item_dir, r))

    header = (
        f"# Social digest ({dt.datetime.now():%Y-%m-%d %H:%M})\n\n"
        f"{len(urls)} links. Per-link folders sit next to this file; view images there.\n\n"
    )
    digest = out / "digest.md"
    digest.write_text(header + "\n---\n\n".join(sections), encoding="utf-8")
    print(digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
