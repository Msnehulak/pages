# Snehulak.dev

Vlastní vícejazyčný statický generátor (Python + Jinja2 + Markdown + Tailwind CSS).

## Požadavky

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Node.js 26 + npm

## Lokální build

```bash
cp .env.example .env   # doplň API klíče
uv sync
npm ci
uv run python build.py
```

Výsledek se vygeneruje do `output/`. Náhled spustíš takto:

```bash
uv run python start_server.py
# http://127.0.0.1:8000
```

Build funguje i bez `YOUTUBE_API_KEY` – YouTube karty se v tom případě vykreslí
jako náhledové thumbnaily s přehrávačem (bez metadat z YouTube API).

## GitHub Actions

Workflow [`.github/workflows/deploy-new-core.yml`](.github/workflows/deploy-new-core.yml)
se spouští při pushi a pull requestu do větve `my-engine`, případně ručně přes
`workflow_dispatch`.

- **Build** job nainstaluje Python a Node závislosti, postaví web a nahraje
  `output/` jako artifact.
- **Deploy** job se pustí jen u push/e nebo ručního spuštění a nasadí `output/`
  na Cloudflare Pages přes Wrangler.

### Secrets a variables

V nastavení repozitáře (`Settings → Secrets and variables → Actions`):

| Název | Typ | Povinné | Popis |
| --- | --- | --- | --- |
| `YOUTUBE_API_KEY` | secret | ne | YouTube metadata; bez něj se použije fallback |
| `OSU_CLIENT_ID` | secret | ne | OSU API |
| `OSU_CLIENT_SECRET` | secret | ne | OSU API |
| `STEAM_API` | secret | ne | Steam API |
| `GIT_HUB_TOKEN` | secret | ne | rezervováno pro budoucí použití |
| `CLOUDFLARE_API_TOKEN` | secret | ano (deploy) | token s právem nasazovat Cloudflare Pages |
| `CLOUDFLARE_ACCOUNT_ID` | variable/secret | ano (deploy) | ID účtu Cloudflare |
| `CLOUDFLARE_PROJECT_NAME` | variable/secret | ano (deploy) | název projektu v Cloudflare Pages |
| `SITEURL` | variable | ne | výchozí `https://snehulak.dev` |

Workflow používá `CLOUDFLARE_ACCOUNT_ID` a `CLOUDFLARE_PROJECT_NAME` nejdřív
jako variable, a když nejsou nastavené, zkusí je vzít ze secrets.
