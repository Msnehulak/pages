import functools
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DIRECTORY = ROOT_DIR / "output"

if not DIRECTORY.is_dir():
    raise SystemExit(
        f"Chyba: {DIRECTORY} neexistuje. Nejdřív spusť build (python build.py)."
    )

handler = functools.partial(SimpleHTTPRequestHandler, directory=str(DIRECTORY))
httpd = HTTPServer(("", 8000), handler)

print(f"Serving {DIRECTORY} on http://127.0.0.1:8000/")
httpd.serve_forever()
