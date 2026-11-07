import json
from functools import partial
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlmodel import Session, create_engine, select

from . import pages_db
from .modules import social_link, yt_iframe

root_dir = Path(__file__).parent.parent.resolve()
theme_dir = root_dir / "theme"
jinja_values_dir = root_dir / "data" / "jinja_values"

MD_EXTENSIONS = ["extra", "fenced_code", "tables", "attr_list"]


class PagesBuilder:
    def __init__(self) -> None:
        self.db_engine = create_engine("sqlite:///ssg.db")
        self.theme_env = Environment(
            loader=FileSystemLoader(theme_dir),
            autoescape=select_autoescape(["html"]),
        )
        self.content_env = Environment(autoescape=False)

    def main(self):
        with Session(self.db_engine) as session:
            pages = session.exec(select(pages_db.Page)).all()

        for page in pages:
            self.build_page(page)

    @staticmethod
    def clear_link(link: str):
        link = link.strip("/")
        link = f"/{link}/"
        while "//" in link:
            link = link.replace("//", "/")
        return link

    def build_page(self, page: pages_db.Page):
        # jv = jinja variabls
        jv_global = {
            "page": {
                "title": page.title,
                "description": page.description,
                "url": page.url,
                "lang": page.lang,
                "trans": page.lang_versions,
            },
            "link": self.clear_link,
        }
        jv_page = {
            **jv_global,
            "hello": "hi markdown",
            "tools": {
                "links": partial(social_link.get_social, lang=page.lang),
            },
            "yt": {
                "video": partial(yt_iframe.yt_iframe, lang=page.lang),
            },
        }
        jv_html = {
            **jv_global,
            **self.load_jinja_values(),
            "hello": "hello htlm",
        }
        content_md = self.content_env.from_string(page.content).render(**jv_page)

        # 2) Markdown -> HTML
        content_html = markdown.markdown(content_md, extensions=MD_EXTENSIONS)

        # 3) Obalit theme/base.html
        template = self.theme_env.get_template("base.html")
        html = template.render(content=content_html, **jv_html)

        # 4) Zapsat na page.save_as (už obsahuje output/.../index.html)
        out_path = Path(page.save_as)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        print(f"[OK] {page.url} -> {out_path}")

    def load_jinja_values(self):
        variabls = {}
        for file in jinja_values_dir.iterdir():
            if not file.is_file():
                continue

            if file.suffix == ".json":
                data = json.loads(file.read_text(encoding="utf-8"))
            elif file.suffix in (".yaml", ".yml"):
                data = yaml.safe_load(file.read_text(encoding="utf-8"))
            else:
                continue

            variabls[file.stem] = data

        return {"data": variabls}
