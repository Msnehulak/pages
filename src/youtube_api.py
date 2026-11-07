import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from . import cache_manager

CACHE_TIMER = 1 * 60 * 60

_MISSING = object()


class YouTubeAPIWrapper:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("Chybí YOUTUBE_API_KEY v proměnných prostředí (.env).")

        self.cache = cache_manager.get_cache()
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def get_channel_by_id(self, channel_id: str) -> dict | None:
        """Získá základní informace o kanálu podle jeho ID."""
        try:
            cache_name = f"yt_api_chanel_{channel_id}"
            cached = self.cache.get(cache_name, default=_MISSING)
            if cached is not _MISSING:
                return cached

            response = (
                self.youtube.channels()
                .list(part="snippet,statistics,brandingSettings", id=channel_id)
                .execute()
            )

            items = response.get("items", [])
            if not items:
                self.cache.set(cache_name, None, expire=60 * 15)  # 15 min
                return None

            channel = items[0]
            snippet = channel.get("snippet", {})
            statistics = channel.get("statistics", {})

            pp = snippet.get("thumbnails", {})
            pp_download_url = pp["high"]["url"]
            pp_url = cache_manager.download_img(
                pp_download_url, f"yt_api_video_{channel_id}.jpeg"
            )

            ret = {
                "channel_id": channel_id,
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "custom_url": snippet.get("customUrl"),
                "published_at": snippet.get("publishedAt"),
                "thumbnails": pp_url,
                "subscriber_count": statistics.get("subscriberCount"),
                "video_count": statistics.get("videoCount"),
            }
            self.cache.set(cache_name, ret, expire=CACHE_TIMER)
            return ret

        except HttpError as e:
            print(f"Chyba při komunikaci s YouTube API (Channel): {e}")
            return None

    def get_video_by_id(self, video_id: str) -> dict | None:
        """Získá informace o videu podle jeho ID."""
        try:
            cache_name = f"yt_api_video_{video_id}"
            cached = self.cache.get(cache_name, default=_MISSING)
            if cached is not _MISSING:
                return cached

            response = (
                self.youtube.videos()
                .list(part="snippet,statistics,contentDetails", id=video_id)
                .execute()
            )

            items = response.get("items", [])
            if not items:
                self.cache.set(cache_name, None, expire=60 * 15)  # 15 min
                return None

            video = items[0]
            snippet = video.get("snippet", {})
            statistics = video.get("statistics", {})

            thumbnails = snippet.get("thumbnails", {})
            thumbnail_download_url = thumbnails["high"]["url"]
            thumbnail_utl = cache_manager.download_img(
                thumbnail_download_url, f"yt_api_video_{video_id}.jpeg"
            )

            ret = {
                "video_id": video_id,
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "channel_id": snippet.get("channelId"),
                "channel_title": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "thumbnails": thumbnail_utl,
                "view_count": statistics.get("viewCount"),
                "like_count": statistics.get("likeCount"),
                "comment_count": statistics.get("commentCount"),
            }
            self.cache.set(cache_name, ret, expire=CACHE_TIMER)
            return ret

        except HttpError as e:
            print(f"Chyba při komunikaci s YouTube API (Video): {e}")
            return None

    def get_video_with_creator(self, video_id: str) -> dict | None:
        """Z വർce z ID videa vrátí jak informace o videu, tak detailní informace o tvůrci (kanálu)."""
        video_info = self.get_video_by_id(video_id)
        if not video_info:
            return None

        channel_id = video_info.get("channel_id")
        creator_info = None
        if channel_id:
            creator_info = self.get_channel_by_id(channel_id)

        return {"video": video_info, "creator": creator_info}


# Pomocná instance nebo funkce pro zpětnou kompatibilitu s tvým kódem v yt_iframe.py
_client = None


def get_client() -> YouTubeAPIWrapper:
    global _client
    if _client is None:
        _client = YouTubeAPIWrapper()
    return _client


def get_video_with_creator(video_id: str) -> dict | None:
    return get_client().get_video_with_creator(video_id)
