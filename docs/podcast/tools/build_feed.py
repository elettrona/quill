#!/usr/bin/env python3
"""Build the QUILL Cast RSS feed and the accessible episode index page.

Reads ``docs/podcast/episodes.json`` (series + episode metadata),
``docs/podcast/audio/durations.json`` (written by generate_kokoro.py), and the
generated MP3 files (for byte sizes), then writes:

* ``docs/site/podcast/feed.xml`` — RSS 2.0 with iTunes tags, enclosures
  pointing at the ``podcast-v1`` GitHub release assets.
* ``docs/site/podcast/index.html`` — a plain, accessible episode list with
  links to the audio and the full transcripts.
* ``docs/site/podcast/transcripts/<slug>.html`` — one accessible page per
  transcript.

Usage::

    python docs/podcast/tools/build_feed.py
"""

from __future__ import annotations

import email.utils
import html
import json
import re
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
PODCAST_ROOT = HERE.parent
REPO_ROOT = PODCAST_ROOT.parent.parent
AUDIO_DIR = PODCAST_ROOT / "audio"
SCRIPTS_DIR = PODCAST_ROOT / "scripts"
SITE_DIR = REPO_ROOT / "docs" / "site" / "podcast"

_SPEAKER = re.compile(r"^\[(LIAM|JESSICA|PAUSE)\]$")


def _rfc2822(iso: str) -> str:
    moment = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return email.utils.format_datetime(moment)


def _duration_hms(seconds: float) -> str:
    total = int(round(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _transcript_html(slug: str, title: str, site_title: str) -> str:
    lines = (SCRIPTS_DIR / f"{slug}.txt").read_text(encoding="utf-8").splitlines()
    body: list[str] = []
    current: str | None = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal buf
        if current and buf:
            body.append(
                f"<p><strong>{html.escape(current.title())}:</strong> "
                + html.escape(" ".join(buf))
                + "</p>"
            )
        buf = []

    for raw in lines:
        text = raw.strip()
        if not text:
            continue
        match = _SPEAKER.match(text)
        if match is None:
            buf.append(text)
            continue
        flush()
        marker = match.group(1)
        if marker == "PAUSE":
            body.append("<hr>")
            current = None
        else:
            current = marker
    flush()
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{html.escape(title)} - transcript - {html.escape(site_title)}</title>\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "</head>\n<body>\n<main>\n"
        f"<h1>{html.escape(title)} - transcript</h1>\n"
        '<p><a href="../index.html">Back to all episodes</a></p>\n'
        + "\n".join(body)
        + "\n</main>\n</body>\n</html>\n"
    )


def main() -> int:
    meta = json.loads((PODCAST_ROOT / "episodes.json").read_text(encoding="utf-8"))
    show = meta["podcast"]
    episodes = meta["episodes"]
    durations: dict[str, float] = {}
    durations_path = AUDIO_DIR / "durations.json"
    if durations_path.exists():
        durations = json.loads(durations_path.read_text(encoding="utf-8"))

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "transcripts").mkdir(exist_ok=True)

    items: list[str] = []
    index_rows: list[str] = []
    now = email.utils.format_datetime(datetime.now(UTC))

    for episode in episodes:
        slug = episode["slug"]
        title = episode["title"]
        description = episode["description"]
        audio_url = show["audio_base_url"] + f"{slug}.mp3"
        transcript_url = show["site_url"] + f"transcripts/{slug}.html"
        mp3 = AUDIO_DIR / f"{slug}.mp3"
        size = mp3.stat().st_size if mp3.exists() else 0
        duration = durations.get(slug, 0.0)

        items.append(
            "    <item>\n"
            f"      <title>{html.escape(title)}</title>\n"
            f"      <description>{html.escape(description)} "
            f"Full transcript: {html.escape(transcript_url)}</description>\n"
            f"      <link>{html.escape(transcript_url)}</link>\n"
            f'      <guid isPermaLink="false">quill-cast-{slug}</guid>\n'
            f"      <pubDate>{_rfc2822(episode['pubdate'])}</pubDate>\n"
            f'      <enclosure url="{html.escape(audio_url)}" '
            f'length="{size}" type="audio/mpeg"/>\n'
            f"      <itunes:duration>{_duration_hms(duration)}</itunes:duration>\n"
            f"      <itunes:explicit>false</itunes:explicit>\n"
            "    </item>"
        )
        minutes = f"{duration / 60:.0f} minutes" if duration else "duration pending"
        index_rows.append(
            "<li>"
            f"<h2>{html.escape(title)}</h2>"
            f"<p>{html.escape(description)}</p>"
            f'<p><a href="{html.escape(audio_url)}">Listen (MP3, {minutes})</a> | '
            f'<a href="transcripts/{slug}.html">Read the transcript</a></p>'
            "</li>"
        )
        (SITE_DIR / "transcripts" / f"{slug}.html").write_text(
            _transcript_html(slug, title, show["title"]), encoding="utf-8"
        )

    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" '
        'xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{html.escape(show['title'])}</title>\n"
        f"    <link>{html.escape(show['site_url'])}</link>\n"
        f"    <description>{html.escape(show['description'])}</description>\n"
        f"    <language>{show['language']}</language>\n"
        f"    <lastBuildDate>{now}</lastBuildDate>\n"
        f'    <atom:link href="{html.escape(show["site_url"] + "feed.xml")}" '
        f'rel="self" type="application/rss+xml"/>\n'
        f"    <itunes:author>{html.escape(show['author'])}</itunes:author>\n"
        f"    <itunes:subtitle>{html.escape(show['subtitle'])}</itunes:subtitle>\n"
        f"    <itunes:summary>{html.escape(show['description'])}</itunes:summary>\n"
        f"    <itunes:explicit>false</itunes:explicit>\n"
        f'    <itunes:category text="{html.escape(show["category"])}"/>\n'
        f"    <itunes:owner><itunes:name>{html.escape(show['author'])}</itunes:name>"
        f"<itunes:email>{html.escape(show['email'])}</itunes:email></itunes:owner>\n"
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )
    (SITE_DIR / "feed.xml").write_text(feed, encoding="utf-8")

    index = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{html.escape(show['title'])}</title>\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<link rel="alternate" type="application/rss+xml" '
        f'title="{html.escape(show["title"])}" href="feed.xml">\n'
        "</head>\n<body>\n<main>\n"
        f"<h1>{html.escape(show['title'])}</h1>\n"
        f"<p>{html.escape(show['description'])}</p>\n"
        '<p><a href="feed.xml">Subscribe with the RSS feed</a> in any podcast app.</p>\n'
        "<ul>\n" + "\n".join(index_rows) + "\n</ul>\n"
        "</main>\n</body>\n</html>\n"
    )
    (SITE_DIR / "index.html").write_text(index, encoding="utf-8")

    print(f"Wrote {SITE_DIR / 'feed.xml'}")
    print(f"Wrote {SITE_DIR / 'index.html'} and {len(episodes)} transcript pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
