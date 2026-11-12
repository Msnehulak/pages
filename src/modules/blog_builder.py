from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

root_dir = Path(__file__).parent.parent.parent.resolve()
theme_dir = root_dir / "theme"

VALID_STYLES = {"list", "grid"}

# Vlastní Jinja env jen pro komponentu blogs.html
_blogs_env = Environment(
    loader=FileSystemLoader(theme_dir),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_blogs(
    pages,
    lang: str = "en",
    style: str = "list",
) -> str:
    """Vrátí HTML se seznamem blogových příspěvků pro daný jazyk."""
    if style not in VALID_STYLES:
        style = "list"

    blog_pages = [
        page
        for page in pages
        if getattr(page, "category", None) == "blog" and page.lang == lang
    ]
    # Nejnovější příspěvky první. create_at je text ve formátu "YYYY MM.DD";
    # příspěvky bez data mají "100", takže skončí na konci.
    blog_pages.sort(
        key=lambda page: (page.create_at or {}).get("unix", 0),
        reverse=True,
    )
    template = _blogs_env.get_template("components/blogs.html")
    return template.module.render_blogs(
        blog_pages,
        lang=lang,
        style=style,
    )
