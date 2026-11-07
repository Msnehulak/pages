from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
from pathlib import Path

from tailwindcss_bin import apply_node_path, find_tailwindcss_bin

apply_node_path()

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "output"
INPUT_CSS = ROOT_DIR / "theme" / "tailwind.css"
OUTPUT_CSS = OUTPUT_DIR / "assets" / "tailwind.css"
TAILWIND_BIN = ROOT_DIR / "node_modules" / ".bin" / "tailwindcss"


class RunNode:
    def __init__(self) -> None:
        pass

    def tailwind(
        self,
        inp=ROOT_DIR / "theme" / "tailwind.css",
        out=OUTPUT_DIR / "assets" / "tailwind.css",
    ):
        subprocess.run(
            [
                find_tailwindcss_bin(),
                "-i",
                inp,
                "-o",
                out,
                "--minify",
            ],
            check=True,
        )
        logging.info(f"tailwind build is good")

    def type_script(self):
        path = f"{OUTPUT_DIR / 'assets' / 'ts'}/*.ts"
        result = subprocess.run(
            [
                "npx",
                "tsc",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        logging.info("Type Script run")


run = RunNode()
