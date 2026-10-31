# SoyMate web app

React + TypeScript + Vite frontend for the SoyMate demo. It talks to the FastAPI backend in `app/api`
through relative URLs (`/api/...`, contract in `app/API.md`), so in production it must be served from the
same origin as the API.

## Develop

```bash
npm install
npm run dev:mock        # same as VITE_MOCK=1 npm run dev: no backend needed
npm run dev             # real API: /api is proxied to http://localhost:8000
API_PROXY=http://<box>:8000 npm run dev   # proxy to another backend
```

## Mock mode

`VITE_MOCK=1` swaps the API client for `src/mocks/` (loaded with a dynamic import, so it is not in the
production bundle). A "Mock data" badge shows in the header. Seed outlines come from our segmenter on a
local Ghana photo; classes and probabilities are random placeholders. Evidence cards are the output of
`app/api/evidence.py` (`src/mocks/evidence.json`; regenerate with
`python3 -c "import sys,json; sys.path.insert(0,'app/api'); import evidence; print(json.dumps(evidence.build(), indent=1))"`
from the repo root). Upload a file whose name contains `noseed` or `down` to see the error states.

## Build

```bash
npm run build           # type check + build to dist/
npm run preview         # serve dist/ locally
```

Serve `dist/` at `/` with the API at `/api` on the same host. Routing is hash-based (`#/trust`,
`#/about`), so no server rewrite rules are needed.
