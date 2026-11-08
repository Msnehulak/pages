import argparse
import logging
import os
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"
DB_PATH = ROOT_DIR / "ssg.db"


def main() -> int:
    parser = argparse.ArgumentParser(description="Postaví statický web do output/.")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument(
        "--log",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        type=str.upper,
        help="Nastaví úroveň logování: DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )
    args = parser.parse_args()  # ← jen jednou
    logging.basicConfig(
        level=args.log,  # už je velkými písmeny díky type=str.upper
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    # Všechny relativní cesty (ssg.db, output/, theme/static) míří do kořene
    # projektu, i když build spustíš odjinud.
    os.chdir(ROOT_DIR)

    # Build musí být opakovatelný: stará databáze i výstup by jinak
    # způsobily UNIQUE constraint chyby a zůstaly by v nich smazané stránky.
    if DB_PATH.exists():
        DB_PATH.unlink()
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
        logging.info("Remove output/ folder")

    from src import (
        cache_manager,
        create_sitemap,
        index_content,
        mearge_page,
        pages_bulder,
        pages_db,
        run_node,
    )

    if args.no_cache:
        cache_manager.get_cache().clear()
        logging.info("Cache is empty")

    pages_db.init_sqlite_DB()

    index_content.IndexContent()

    mearge_page.link_language_versions()

    create_sitemap.generate_sitemap()

    pages_bulder.PagesBuilder().main()

    run_node.run.tailwind()
    run_node.run.type_script()

    src = ROOT_DIR / "theme" / "static"
    dst = OUTPUT_DIR / "static"
    if dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
