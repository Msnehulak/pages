import os

from dotenv import load_dotenv

load_dotenv()

_site_url = None


def get_siteurl(type: str = "main"):
    global _site_url
    if _site_url == None:
        _site_url = os.getenv("SITEURL", "https://example.com").rstrip("/")
    return _site_url
