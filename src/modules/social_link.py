from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

root_dir = Path(__file__).parent.parent.parent.resolve()
socials_file = root_dir / "data" / "socials.yaml"
theme_dir = root_dir / "theme"

with open(socials_file, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f) or {}

all_data = {"all_data": data}

SOCIALS = data.get("socials", [])

VALID_STYLES = {"full", "icon", "text", "pill", "profile"}

# Vlastní Jinja env jen pro komponentu links.html
_links_env = Environment(
    loader=FileSystemLoader(theme_dir),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_social(tag: str = "all", lang: str = "en", style: str = "full") -> str:
    """Vrátí HTML se seznamem sociálních odkazů vyfiltrovaných podle tagu."""
    if style not in VALID_STYLES:
        style = "full"

    filtered = [s for s in SOCIALS if tag == "all" or tag in (s.get("tags") or [])]
    if not filtered:
        return ""

    template = _links_env.get_template("components/links.html")
    return template.module.render_links(
        filtered,
        lang=lang,
        style=style,
        **all_data,
    )
