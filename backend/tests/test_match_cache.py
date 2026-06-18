"""Tests for the Spotify->YouTube match cache."""

from datetime import datetime, timedelta, timezone

from replaylist.transfer.match_cache import MatchCache
from replaylist.youtube import YouTubeVideo


def _video(vid="yt1"):
    return YouTubeVideo(
        id=vid, title="Song", channel_title="Artist",
        duration="", published_at="", thumbnail_url="",
    )


def test_put_match_hit(tmp_path):
    c = MatchCache(path=tmp_path / "c.json")
    c.put_match("sp1", _video("ytA"), score=200)
    status, video = c.lookup("sp1")
    assert status == "hit"
    assert video.id == "ytA"


def test_put_miss_within_ttl(tmp_path):
    c = MatchCache(path=tmp_path / "c.json", negative_ttl_days=30)
    c.put_miss("sp2")
    status, video = c.lookup("sp2")
    assert status == "miss"
    assert video is None


def test_expired_miss_becomes_unknown(tmp_path):
    c = MatchCache(path=tmp_path / "c.json", negative_ttl_days=30)
    c.put_miss("sp3")
    old = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
    c._entries["sp3"]["updated_at"] = old
    assert c.lookup("sp3")[0] == "unknown"


def test_unknown_when_absent(tmp_path):
    c = MatchCache(path=tmp_path / "c.json")
    assert c.lookup("missing")[0] == "unknown"


def test_invalidate(tmp_path):
    c = MatchCache(path=tmp_path / "c.json")
    c.put_match("sp4", _video("ytD"))
    c.invalidate("sp4")
    assert c.lookup("sp4")[0] == "unknown"


def test_save_reload_roundtrip(tmp_path):
    p = tmp_path / "c.json"
    c = MatchCache(path=p)
    c.put_match("sp5", _video("ytE"), score=150)
    c.put_miss("sp6")
    c.save()

    c2 = MatchCache(path=p)
    status, video = c2.lookup("sp5")
    assert status == "hit" and video.id == "ytE"
    assert c2.lookup("sp6")[0] == "miss"


def test_corrupt_file_starts_empty(tmp_path):
    p = tmp_path / "c.json"
    p.write_text("{not valid json", encoding="utf-8")
    c = MatchCache(path=p)
    assert c.lookup("anything")[0] == "unknown"
