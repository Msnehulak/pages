import os
import re
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


class IndexContent:  # Opraveno: velká počáteční písmena (konvence pro třídy)
    def __init__(self) -> None:  # Opraveno: None s velkým N
        self.index_func = {".md": self.index_mark_down}
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

    def index_mark_down(self, path: Path):
        page = frontmatter.load(path)
        page_content = page.content

        html_content = markdown.markdown(page.content)

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

        print(md_link_deps)

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
        page_url = f"{site_url}/{page_path}"

        page_id = f"{lang}{slug}"

        page_row = pages_db.Page(
            id=page_id,
            slug=slug,
            content=page_content,
            lang=lang,
            title=title,
            description=description,
            jija_dependencys=jija_dependencys,
            md_link_dependencys=md_link_deps,
            md_source_dependencys=md_source_deps,
            url=page_url,
            save_as=str(page_save_as),
            path=page_path,
        )

        with Session(self.db_engine) as session:
            session.add(page_row)
            session.commit()
            print(f"Záznam '{slug}' úspěšně přidán!")
