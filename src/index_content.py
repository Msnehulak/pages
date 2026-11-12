import hashlib
import logging
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import frontmatter
import markdown
from dotenv import load_dotenv
from jinja2 import Environment, meta
from sqlmodel import Session, create_engine

from . import pages_db

load_dotenv()

REGEX = {
    "link": r"(?<!\!)\[(.*?)\]\((.*?)\)",
    "source": r"!\[(.*?)\]\((.*?)\)(?:\{(.*?)\})?",
}

site_url = os.getenv("SITEURL", "https://example.com").rstrip("/")
root_dir = Path(__file__).parent.parent.resolve()
content_dir = root_dir / "content"
output_dir = root_dir / "output"


def get_sha256(filepath):
    with open(filepath, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


class IndexContent:  # Opraveno: velká počáteční písmena (konvence pro třídy)
    def __init__(self) -> None:  # Opraveno: None s velkým N
        self.index_func = {
            ".md": self.index_mark_down,
            ".png": self.index_img,
            ".svg": self.index_svg,
        }
        self.db_engine = create_engine("sqlite:///ssg.db")
        self.jinja2_env = Environment()
        self.main()

    def main(self):
        content_list = []

        for i in content_dir.rglob("*"):
            if i.is_file():
                if i.suffix in self.index_func:
                    self.index_func[i.suffix](i)
                    content_list.append(i)

        print(content_list)

    def markdown_dependencies(self, page_content):
        md_source_deps = []
        md_source_deps_list = re.findall(REGEX["source"], page_content)
        for dep in md_source_deps_list:
            md_source_deps.append(
                {
                    "text": dep[0],
                    "link": dep[1],
                    "extra": dep[2] if len(dep) > 2 else None,
                }
            )

        md_link_deps = []
        md_link_deps_list = re.findall(REGEX["link"], page_content)
        for dep in md_link_deps_list:
            md_link_deps.append(
                {
                    "link": dep[1],
                    "text": dep[0],
                }
            )

        return md_link_deps, md_source_deps

    @staticmethod
    def get_git_file_dates(file_path):
        try:
            cmd_created = [
                "git",
                "log",
                "--follow",
                "--format=%at",
                "--",
                file_path,
            ]
            res_created = subprocess.run(
                cmd_created, capture_output=True, text=True, check=True
            )
            time_stamps = res_created.stdout.splitlines()

            if not time_stamps:
                raise ValueError("git log returned no timestamps")

            create_at_s = int(time_stamps[-1])
            last_update_s = int(time_stamps[0])
        except Exception:
            create_at_s = int(time.time())
            last_update_s = int(time.time())

        def _make(ts: int) -> dict:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            return {
                "unix": ts,  # 1700000000
                "web": dt.isoformat(timespec="seconds"),  # "2023-11-14T22:13:20+00:00"
                "time": dt.strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                ),  # "2023-11-14 22:13:20 UTC"
            }

        create_at = _make(create_at_s)
        last_update = _make(last_update_s)

        return create_at, last_update

    def index_mark_down(self, path: Path):
        page = frontmatter.load(path)
        page_content = page.content

        md_link_deps, md_source_deps = self.markdown_dependencies(page_content)
        html_content = markdown.markdown(page.content)

        page_variables = self.jinja2_env.parse(page_content)
        jija_dependencys = list(meta.find_undeclared_variables(page_variables))

        lang = page.metadata.get("lang", path.stem)
        slug = page.metadata.get("slug", path.stem)
        description = page.metadata.get("description", "No description")
        title = page.metadata.get("title", "No title")
        save_as = page.metadata.get("save_as", None)

        if lang == "en":
            path_lang = ""
        else:
            path_lang = f"{lang}/"

        if save_as == "index":
            page_path = f"{path_lang}"
        else:
            page_path = f"{path_lang}{slug}/"

        page_save_as = output_dir / page_path / "index.html"
        if page_path == "":
            page_url = f"{site_url}"
        else:
            page_url = f"{site_url}/{page_path}"

        page_id = f"{lang}{slug}"

        create_at, last_update = self.get_git_file_dates(str(path))

        page_row = pages_db.Page(
            id=page_id,
            slug=slug,
            content=page_content,
            lang=lang,
            title=title,
            description=description,
            category=page.metadata.get("category", None),
            jija_dependencys=jija_dependencys,
            md_link_dependencys=md_link_deps,
            md_source_dependencys=md_source_deps,
            url=page_url,
            save_as=str(page_save_as),
            path=page_path,
            create_at=create_at,
            last_update=last_update,
        )

        with Session(self.db_engine) as session:
            session.add(page_row)
            session.commit()
            logging.info(f"Indexing as md '{slug}' is corect!")

    def index_img(self, path: Path):
        img_path = str(path)

        img_id = get_sha256(path)

        create_at, last_update = 10, 10  # self.get_git_file_dates(str(path))

        img_row = pages_db.Images(
            id=img_id,
            suffix=path.suffix,
            stem=path.stem,
            create_at=create_at,
            last_update=last_update,
            file_path=img_path,
        )

        with Session(self.db_engine) as session:
            session.add(img_row)
            session.commit()
            logging.info(f"Indexing as md '{path.name}' is corect!")

    def index_svg(self, path: Path):
        pass
