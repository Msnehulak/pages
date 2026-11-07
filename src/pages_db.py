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

    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    lang_versions: dict = Field(default={}, sa_column=Column(JSON))
    jija_dependencys: List[str] = Field(default=[], sa_column=Column(JSON))
    md_link_dependencys: List[dict] = Field(default=[], sa_column=Column(JSON))
    md_source_dependencys: List[dict] = Field(default=[], sa_column=Column(JSON))

    save_as: str
    url: str
    path: str


def init_sqlite_DB():
    engine = create_engine("sqlite:///ssg.db")
    SQLModel.metadata.create_all(engine)
