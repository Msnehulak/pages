# cache_manager.py
import os
from pathlib import Path

import requests
from diskcache_community import Cache, SafeDisk
from dotenv import load_dotenv

load_dotenv()

site_url = os.getenv("SITEURL", "https://example.com").rstrip("/")

root_dir = Path(__file__).parent.parent.resolve()
output_dir = root_dir / "output"

IMG_CACHE_EXPIRE = 7 * 24 * 60 * 60
IMG_PATH = "assets/external"
IMG_PATH_A = output_dir / IMG_PATH

IMG_PATH_A.mkdir(parents=True, exist_ok=True)

_MISSING = object()
_cache_instance = None


def get_cache() -> Cache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = Cache(root_dir / "cache", disk=SafeDisk)
    return _cache_instance


def download_img(url: str, name: str):
    img = download_img_binary(url)
    path = IMG_PATH_A / name
    save_url = f"{site_url}/{IMG_PATH}/{name}"

    with open(path, "wb") as f:
        print(f"write to {path}")
        f.write(img)

    return save_url


def download_img_binary(url: str):
    cache_name = f"img_download_{url}"
    cache = get_cache()
    cached = cache.get(cache_name, default=_MISSING)
    if cached is not _MISSING:
        return cached

    response = requests.get(url)
    response.raise_for_status()

    cache.set(cache_name, response.content, expire=IMG_CACHE_EXPIRE)
    return response.content
