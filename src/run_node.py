#!/usr/bin/env python3
"""Spustí Tailwind CSS přes Node nad už postaveným output/.

Instalaci Tailwindu řeší npm (`npm install`), Python jen ověří, že příkaz
existuje, a spustí ho. Pouští se až na konci buildu, kdy je hotová output/.

Použití:
    python -m src.run_node
    python -m src.run_node --watch
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "output"
INPUT_CSS = ROOT_DIR / "theme" / "tailwind.css"
OUTPUT_CSS = OUTPUT_DIR / "assets" / "tailwind.css"
TAILWIND_BIN = ROOT_DIR / "node_modules" / ".bin" / "tailwindcss"


def run_tailwind(watch: bool = False) -> Path:
    """Vygeneruje CSS z už postaveného output/ a vrátí cestu k němu."""
    if not OUTPUT_DIR.is_dir() or not any(OUTPUT_DIR.rglob("*.html")):
        raise SystemExit(
            "Chyba: output/ neexistuje nebo v něm nejsou HTML soubory. "
            "Nejdřív spusť build (python build.py)."
        )

    if not INPUT_CSS.is_file():
        raise SystemExit(f"Chyba: chybí vstupní CSS: {INPUT_CSS.relative_to(ROOT_DIR)}")

    if shutil.which("node") is None:
        raise SystemExit("Chyba: Node.js není v PATH. Nainstaluj ho (https://nodejs.org).")

    if not TAILWIND_BIN.is_file():
        raise SystemExit(
            "Chyba: Tailwind není nainstalovaný.\n"
            "Spusť v kořeni projektu: npm install"
        )

    OUTPUT_CSS.parent.mkdir(parents=True, exist_ok=True)

    command = [
        str(TAILWIND_BIN),
        "--input",
        str(INPUT_CSS),
        "--output",
        str(OUTPUT_CSS),
        "--minify",
    ]
    if watch:
        command.append("--watch")

    print(f"[tailwind] {OUTPUT_CSS.relative_to(ROOT_DIR)}")
    subprocess.run(command, cwd=ROOT_DIR, check=True)
    return OUTPUT_CSS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Spustí Tailwind CLI a vygeneruje CSS pro output/."
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="sledovat změny v output/ a přegenerovávat CSS",
    )
    args = parser.parse_args(argv)

    run_tailwind(watch=args.watch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
