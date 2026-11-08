import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlmodel import Session, create_engine, select

from . import pages_db, utility

root_dir = Path(__file__).parent.parent.resolve()
sitemap_path = root_dir / "output" / "sitemap.xml"
theme_dir = root_dir / "theme"

_links_env = Environment(
    loader=FileSystemLoader(theme_dir),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def generate_sitemap():
    engine = create_engine("sqlite:///ssg.db")

    with Session(engine) as session:
        pages = session.exec(select(pages_db.Page)).all()

        template = _links_env.get_template("components/sitemap.html")

        sitemap = template.module.render_sitemap(pages)

        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(sitemap)
