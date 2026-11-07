import argparse
import os
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"
DB_PATH = ROOT_DIR / "ssg.db"


def main() -> int:
    parser = argparse.ArgumentParser(description="Postaví statický web do output/.")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    # Všechny relativní cesty (ssg.db, output/, theme/static) míří do kořene
    # projektu, i když build spustíš odjinud.
    os.chdir(ROOT_DIR)

    # Build musí být opakovatelný: stará databáze i výstup by jinak
    # způsobily UNIQUE constraint chyby a zůstaly by v nich smazané stránky.
    if DB_PATH.exists():
        DB_PATH.unlink()
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    from src import (
        cache_manager,
        index_content,
        mearge_page,
        pages_bulder,
        pages_db,
        run_node,
    )

    if args.no_cache:
        cache_manager.get_cache().clear()

    pages_db.init_sqlite_DB()

    index_content.IndexContent()

    mearge_page.link_language_versions()

    pages_bulder.PagesBuilder().main()

    # Tailwind až nakonec, nad hotovým output/
    run_node.run_tailwind()

    src = ROOT_DIR / "theme" / "static"
    dst = OUTPUT_DIR / "static"
    if dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
