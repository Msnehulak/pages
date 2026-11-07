from sqlmodel import Session, create_engine, select

from . import pages_db


def link_language_versions():
    engine = create_engine("sqlite:///ssg.db")

    with Session(engine) as session:
        pages = session.exec(select(pages_db.Page)).all()

        slug_groups = {}
        for page in pages:
            if page.slug not in slug_groups:
                slug_groups[page.slug] = []

            slug_groups[page.slug].append(page)
            print(f"{page.slug} - {page.lang}")

        for group in slug_groups.values():
            lang_map = []
            for x in group:
                lang_map.append({"lang": x.lang, "path": x.path})

            for page in group:
                page.lang_versions = lang_map
                session.add(page)

        session.commit()
        print("[OK] Jazykové verze stránek byly úspěšně propojeny!")
