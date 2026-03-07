# AI-Powered Customer Experience (CX) Analytics Platform

Full-stack CX analytics and journey intelligence project with a working FastAPI backend, Next.js frontend, and a lightweight AI analytics layer.

## Work Completed So Far

### Backend (FastAPI)
- Implemented API server with CORS, startup initialization, and global error handling.
- Implemented data upload and analysis flow:
  - `POST /upload-data` (CSV/JSON upload)
  - `POST /analyze-data` (runs preprocessing + analytics pipeline)
- Implemented insights APIs:
  - `GET /insights`
  - `GET /sentiment-trend`
  - `GET /churn-risk`
- Implemented AI query endpoint:
  - `POST /query-ai`
- Implemented runtime API key endpoint:
  - `POST /admin/api-key`

### AI/Analytics Layer
- Preprocessing pipeline for missing CX columns (`customer_id`, `text`, `timestamp`, `ticket_count`, `inactive_days`).
- Rule-based sentiment scoring and sentiment labels.
- Topic/intent detection via keyword clustering.
- Interpretable churn probability model (sigmoid baseline).
- Journey summary generation and local RAG-style answer fallback.
- Vector store integration:
  - Chroma support (HTTP client)
  - In-memory fallback if Chroma is unavailable

### Frontend (Next.js 14 + TypeScript)
- Implemented pages:
  - `/` Landing page
  - `/dashboard`
  - `/analytics`
  - `/journey`
  - `/ai-copilot`
  - `/admin`
- Added reusable UI components (`card`, `button`, `input`, metric cards, chart components, hero section).
- Connected Admin page to backend for upload + analyze + API key update.
- Connected AI Copilot page to `POST /query-ai`.

### Infra and Project Setup
- Dockerized frontend and backend.
- Added `docker-compose.yml` with:
  - frontend
  - backend
  - celery-worker
  - postgres
  - redis
  - chroma
- Added environment configuration via `.env.example`.
- Added backend test suite with end-to-end API flow (`backend/tests/test_api.py`).

## Current Status
- Core MVP flow is working end-to-end:
  1. Upload dataset
  2. Run analysis
  3. View insights/churn/sentiment
  4. Ask questions in AI Copilot
- Some frontend pages currently use static sample content for visualization and can be wired further to live endpoints.

## Tech Stack
- Frontend: Next.js, TypeScript, Tailwind CSS, Framer Motion, Recharts, Three.js
- Backend: FastAPI, SQLAlchemy, Pydantic Settings
- Data/AI: Pandas, ChromaDB, LangChain/OpenAI (optional), local fallback inference modules
- Infra: Docker Compose, Redis, Celery, PostgreSQL

## API Endpoints
- `GET /`
- `POST /upload-data`
- `POST /analyze-data`
- `GET /insights`
- `GET /sentiment-trend`
- `GET /churn-risk`
- `POST /query-ai`
- `POST /admin/api-key`

## Run Locally

### Docker
```bash
cp .env.example .env
docker compose up --build
```

Services:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Chroma: `http://localhost:8001`

### Without Docker
Backend:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Tests
```bash
pytest backend/tests
```

## Notes
- If `OPENAI_API_KEY` is configured, AI Copilot uses LangChain + OpenAI model calls.
- If OpenAI is unavailable, the backend returns deterministic fallback answers based on retrieved context.
- If Chroma is unavailable, vector search falls back to in-memory similarity.
