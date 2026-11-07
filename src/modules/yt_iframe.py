from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .. import youtube_api

root_dir = Path(__file__).parent.parent.parent.resolve()
theme_dir = root_dir / "theme"

VALID_STYLES = {"full", "icon", "text", "pill", "profile"}

_links_env = Environment(
    loader=FileSystemLoader(theme_dir),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def yt_iframe(
    yt_id: str,
    lang: str = "en",
    style: str = "full",
) -> str:
    """Vrátí HTML s YouTube přehrávačem a metadaty videa."""
    if style not in VALID_STYLES:
        style = "full"

    try:
        meta_data = youtube_api.get_video_with_creator(yt_id)
    except Exception as exc:
        # Build nesmí spadnout kvůli chybějícímu API klíči, kvótě nebo výpadku API.
        print(f"[yt_iframe] Metadata pro {yt_id} nejsou dostupná: {exc}")
        meta_data = None

    template = _links_env.get_template("components/yt_iframe.html")
    return template.module.render_iframe(
        yt_id=yt_id,
        md=meta_data,
        lang=lang,
        style=style,
    )
