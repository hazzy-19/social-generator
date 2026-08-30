# The Quiet Authority — Social Generator

Turn long-form source content into platform-ready social posts (image, hashtags,
caption) with a human-in-the-loop approval workflow.

## Repository layout

```
social-generator/
├── backend/          # FastAPI + Postgres API
├── image-service/    # Node/Express wrapper around pexelkit
└── frontend/         # (planned) Vite/React UI
```

- **backend/** — owns the generation lifecycle (create → reload sections →
  approve sections → save) and orchestrates calls to the AI extraction module
  and the image service.
- **image-service/** — standalone Node service that wraps your `pexelkit` npm
  package. FastAPI calls it over HTTP; it is never imported directly from Python.

## Module boundaries (`backend/app/`)

| Module         | Owns                                                   | Never does                        |
|----------------|--------------------------------------------------------|-----------------------------------|
| `generations/` | the DB table, approve/reload/save orchestration        | call the NVIDIA API or pexelkit directly |
| `ai/`          | prompt templates + NVIDIA API calls                    | touch the database                |
| `images/`      | HTTP calls to image-service                            | touch the database                |
| `platforms/`   | character limits + validation, `PlatformType` enum     | depend on any other module        |
| `shared/`      | exceptions and cross-cutting helpers only              | contain business logic            |

Routers → services → repositories, always in that direction. If you find
yourself importing `repository.py` from a router, or importing `ai/` from
`platforms/`, that's a sign the boundary is being crossed — stop and route it
through `service.py` instead.

## Running locally

```bash
# 1. Postgres — create database `socials` if needed

# 2. Backend (from repo root)
cd backend
# .env already holds DATABASE_URL, NVIDIA_API_KEY, etc.
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 3. Image service (separate terminal, from repo root)
cd image-service
# .env already holds PEXELS_API_KEY
npm install
npm run dev

# 4. Frontend (separate terminal, once scaffolded)
cd frontend
npm install
npm run dev
```

## Known TODOs before this is real

- `image-service/src/services/pexelSearch.js` guesses at pexelkit's actual
  exported function/shape — swap in the real call.
- `backend/app/ai/client.py` assumes an OpenAI-compatible chat completion
  response shape for the NVIDIA endpoint — confirm against NVIDIA's actual API
  docs for your chosen model before relying on it.
- No auth yet — every endpoint is open. Fine for local single-author use, not
  fine before this touches the internet.
