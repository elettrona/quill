"""Tests for the publishing core: RSS generation, destinations, Auphonic parsing."""

from __future__ import annotations

from pathlib import Path

from quill.core.publish.auphonic import ProductionStatus, _multipart
from quill.core.publish.destinations import (
    DestinationStore,
    SftpDestination,
    load_destinations,
    save_destinations,
)
from quill.core.publish.rss import FeedItem, generate_rss, write_rss
from quill.core.publish.sftp_publish import companion_files, public_url
from quill.core.speech.ffmpeg import AudioMetadata


def _tags() -> AudioMetadata:
    return AudioMetadata(
        album="My Book", artist="Jane Doe", album_artist="Sam Reader", genre="Fiction"
    )


def _item(tmp_path: Path, *, chapters: bool = False) -> FeedItem:
    audio = tmp_path / "book.m4b"
    audio.write_bytes(b"x" * 1234)
    return FeedItem(
        path=audio,
        media_url="https://example.com/pod/book.m4b",
        title="My Book",
        duration_s=3600,
        has_chapters=chapters,
    )


def test_generate_rss_carries_tags_and_enclosure(tmp_path: Path) -> None:
    xml = generate_rss([_item(tmp_path)], _tags(), feed_url="https://example.com/feed.rss")
    assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "<title>My Book</title>" in xml
    assert 'itunes:category text="Fiction"' in xml
    assert "<itunes:author>Jane Doe</itunes:author>" in xml
    assert "<itunes:author>Sam Reader</itunes:author>" in xml
    assert 'url="https://example.com/pod/book.m4b"' in xml
    assert 'type="audio/x-m4b"' in xml
    assert 'length="1234"' in xml
    assert "<itunes:duration>3600</itunes:duration>" in xml


def test_generate_rss_links_chapters_sidecar(tmp_path: Path) -> None:
    xml = generate_rss([_item(tmp_path, chapters=True)], _tags())
    assert 'url="https://example.com/pod/book.chapters.json"' in xml
    assert 'type="application/json+chapters"' in xml


def test_write_rss_enforces_extension(tmp_path: Path) -> None:
    out = write_rss([_item(tmp_path)], _tags(), tmp_path / "feed.xml")
    assert out.suffix == ".rss" and out.is_file()


def test_destinations_round_trip_without_secrets(tmp_path: Path) -> None:
    store = DestinationStore(
        destinations=[
            SftpDestination(
                name="My host",
                host="example.com",
                username="jeff",
                remote_dir="/pod",
                port=2222,
                url_base="https://example.com/pod",
            )
        ]
    )
    save_destinations(tmp_path, store)
    text = (tmp_path / "publish_destinations.json").read_text(encoding="utf-8")
    assert "password" not in text.lower() and "secret" not in text.lower()
    loaded = load_destinations(tmp_path)
    dest = loaded.find("My host")
    assert dest is not None
    assert dest.port == 2222 and dest.url_base == "https://example.com/pod"
    assert dest.credential_target == "quill:publish:sftp:My host"


def test_load_destinations_tolerates_junk(tmp_path: Path) -> None:
    (tmp_path / "publish_destinations.json").write_text("not json", encoding="utf-8")
    assert load_destinations(tmp_path).destinations == []


def test_public_url_and_companions(tmp_path: Path) -> None:
    dest = SftpDestination(
        name="x", host="h", username="u", remote_dir="/pod", url_base="https://e.com/pod/"
    )
    assert public_url(dest, "book.m4b") == "https://e.com/pod/book.m4b"
    assert public_url(SftpDestination(name="x", host="h", username="u", remote_dir="/"), "b") == ""
    book = tmp_path / "book.m4b"
    book.write_bytes(b"x")
    book.with_suffix(".chapters.json").write_text("{}", encoding="utf-8")
    book.with_suffix(".rss").write_text("<rss/>", encoding="utf-8")
    names = [p.name for p in companion_files(book)]
    assert names == ["book.chapters.json", "book.rss"]


def test_auphonic_multipart_shape(tmp_path: Path) -> None:
    payload = tmp_path / "a.mp3"
    payload.write_bytes(b"AUDIO")
    body, content_type = _multipart({"action": "start", "title": "T"}, "input_file", payload)
    assert content_type.startswith("multipart/form-data; boundary=")
    boundary = content_type.split("boundary=", 1)[1]
    assert body.count(f"--{boundary}".encode()) == 4  # 3 parts + terminator
    assert b'name="action"\r\n\r\nstart' in body
    assert b'filename="a.mp3"' in body
    assert b"AUDIO" in body
    assert body.endswith(f"--{boundary}--\r\n".encode())


def test_auphonic_status_flags() -> None:
    assert ProductionStatus(uuid="u", status=3, status_string="Done").done
    assert ProductionStatus(uuid="u", status=2, status_string="Error").failed
    running = ProductionStatus(uuid="u", status=1, status_string="Processing")
    assert not running.done and not running.failed
