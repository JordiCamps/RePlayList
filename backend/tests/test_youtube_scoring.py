"""Tests for YouTube candidate scoring in find_video_by_metadata."""

from replaylist.youtube import YouTubeAPI, YouTubeVideo


def _v(vid, title, channel):
    return YouTubeVideo(
        id=vid, title=title, channel_title=channel,
        duration="", published_at="", thumbnail_url="",
    )


def test_scorer_prefers_best_over_first(monkeypatch):
    api = YouTubeAPI("dummy")
    # The relevance-first result is a poor cover; the official upload is later.
    candidates = [
        _v("bad", "Bohemian Rhapsody PIANO COVER reaction video", "Random Guy"),
        _v("good", "Bohemian Rhapsody", "Queen"),
    ]
    monkeypatch.setattr(api, "search_videos", lambda q, max_results=50: candidates)
    video, score = api.find_video_by_metadata_scored("Bohemian Rhapsody", "Queen")
    assert video is not None
    assert video.id == "good"


def test_scorer_returns_none_below_threshold(monkeypatch):
    api = YouTubeAPI("dummy")
    candidates = [_v("x", "xxxxxxxx zzzzzzzz", "yyyyyyyy")]
    monkeypatch.setattr(api, "search_videos", lambda q, max_results=50: candidates)
    video, score = api.find_video_by_metadata_scored("Bohemian Rhapsody", "Queen")
    assert video is None


def test_empty_results_returns_none(monkeypatch):
    api = YouTubeAPI("dummy")
    monkeypatch.setattr(api, "search_videos", lambda q, max_results=50: [])
    assert api.find_video_by_metadata_scored("anything", "anyone") == (None, 0)
