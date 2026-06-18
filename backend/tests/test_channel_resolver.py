"""Tests for the artist -> YouTube channel resolver (Phase 2)."""

from replaylist.transfer.channel_resolver import ArtistChannelResolver
from replaylist.youtube import YouTubeVideo


class FakeYT:
    def __init__(self, channels, videos):
        self._channels = channels          # list of (channel_id, title)
        self._videos = videos              # dict channel_id -> [YouTubeVideo]
        self.search_calls = 0

    def search_channels(self, query, max_results=10):
        self.search_calls += 1
        return self._channels

    def get_channel_videos(self, channel_id, max_videos=250):
        return self._videos.get(channel_id, [])


def _v(vid, title, channel="Queen - Topic"):
    return YouTubeVideo(id=vid, title=title, channel_title=channel,
                        duration="", published_at="", thumbnail_url="")


def test_resolves_topic_channel_and_matches(tmp_path):
    yt = FakeYT(
        channels=[("UCqueen", "Queen - Topic"), ("UCother", "Some Cover Channel")],
        videos={"UCqueen": [_v("v1", "Bohemian Rhapsody"), _v("v2", "Don't Stop Me Now")]},
    )
    r = ArtistChannelResolver(yt, path=tmp_path / "ac.json", min_tracks=2)

    video, units = r.find_match("Queen", "Bohemian Rhapsody", artist_track_count=5)
    assert video is not None and video.id == "v1"
    assert units == 100  # one channel resolution search

    # Second track of the same artist: served from the cached pool, no new search.
    video2, units2 = r.find_match("Queen", "Don't Stop Me Now", artist_track_count=5)
    assert video2 is not None and video2.id == "v2"
    assert units2 == 0
    assert yt.search_calls == 1


def test_skips_when_artist_below_threshold(tmp_path):
    yt = FakeYT(channels=[("UCq", "Queen - Topic")], videos={"UCq": [_v("v1", "X")]})
    r = ArtistChannelResolver(yt, path=tmp_path / "ac.json", min_tracks=2)
    video, units = r.find_match("Queen", "X", artist_track_count=1)
    assert video is None and units == 0
    assert yt.search_calls == 0


def test_no_channel_caches_negative(tmp_path):
    yt = FakeYT(channels=[], videos={})
    r = ArtistChannelResolver(yt, path=tmp_path / "ac.json", min_tracks=2)
    v1, u1 = r.find_match("Obscure", "Song", artist_track_count=3)
    assert v1 is None and u1 == 100  # the (empty) search was still made
    v2, u2 = r.find_match("Obscure", "Other", artist_track_count=3)
    assert v2 is None and u2 == 0  # negative cached, no second search
    assert yt.search_calls == 1
