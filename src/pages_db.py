import logging
from typing import List, Optional

from sqlmodel import JSON, Column, Field, Session, SQLModel, create_engine


class Page(SQLModel, table=True):
    __tablename__ = "pages"
    id: str = Field(primary_key=True)
    slug: str

    content: str
    lang: str = Field(default="cs")

    title: str = Field(default="No Title")
    description: str = Field(default="No Description")
    create_at: List[dict] = Field(default=[], sa_column=Column(JSON))
    last_update: List[dict] = Field(default=[], sa_column=Column(JSON))

    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    lang_versions: dict = Field(default={}, sa_column=Column(JSON))
    jija_dependencys: List[str] = Field(default=[], sa_column=Column(JSON))
    md_link_dependencys: List[dict] = Field(default=[], sa_column=Column(JSON))
    md_source_dependencys: List[dict] = Field(default=[], sa_column=Column(JSON))

    category: str | None = Field(default=None)

    save_as: str
    url: str
    path: str


class Images(SQLModel, table=True):
    __tablename__ = "images"
    id: str = Field(primary_key=True)

    suffix: str = Field(default="")
    stem: str = Field(default="")

    create_at: str = Field(default="")
    last_update: str = Field(default="")

    url: str = Field(default="")
    path: str = Field(default="")
    file_path: str


def init_sqlite_DB():
    engine = create_engine("sqlite:///ssg.db")
    SQLModel.metadata.create_all(engine)
    logging.info(f"init SQLite")
