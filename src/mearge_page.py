import logging

from sqlmodel import Session, create_engine, select

from . import pages_db, utility

site_url = utility.get_siteurl()


def link_language_versions():
    engine = create_engine("sqlite:///ssg.db")

    with Session(engine) as session:
        pages = session.exec(select(pages_db.Page)).all()

        slug_groups = {}
        for page in pages:
            if page.slug not in slug_groups:
                slug_groups[page.slug] = []
            slug_groups[page.slug].append(page)

        for group in slug_groups.values():
            lang_map = []
            for x in group:
                lang_url = f"{site_url}/{x.path}"
                lang_map.append(
                    {
                        "lang": x.lang,
                        "path": x.path,
                        "url": lang_url,
                    }
                )

            for page in group:
                page.lang_versions = lang_map
                session.add(page)
                logging.info(f"{page.slug} - {page.lang}")

        session.commit()
