# CX AI Platform

Production-ready, full-stack **Customer Experience (CX) Analytics & Journey Intelligence Platform**.

## Stack
- Frontend: Next.js 14, TypeScript, TailwindCSS, Shadcn-style UI components, Framer Motion, Three.js, Recharts
- Backend: FastAPI, LangChain, OpenAI API integration, Chroma vector DB, PostgreSQL, Redis, Celery
- AI Layer: RAG pipeline, sentiment detection, intent/topic clustering, churn scoring, journey summarization

## Features
- Upload CX data via CSV/JSON
- Analyze customer sentiment, intent, churn probability, and anomalies
- RAG semantic retrieval for contextual AI answers
- Dashboard with sentiment timeline and churn heatmap segments
- Customer Journey Explorer
- AI Copilot (`/query-ai`) for analytics Q&A
- Admin panel for upload and analysis trigger
- Real-time architecture foundation with Redis + Celery worker

## Project Structure
```text
cx-ai-platform/
├ frontend/
│  ├ app/
│  ├ components/
│  ├ dashboard/
│  ├ analytics/
│  ├ ai-copilot/
│  └ styles/
├ backend/
│  ├ main.py
│  ├ api/
│  ├ services/
│  ├ rag/
│  ├ models/
│  ├ workers/
│  └ database/
├ ai-engine/
│  ├ embeddings.py
│  ├ sentiment.py
│  ├ churn_model.py
│  ├ clustering.py
│  └ rag_pipeline.py
├ docker-compose.yml
├ requirements.txt
├ package.json
└ .env.example
```

## API Endpoints
- `POST /upload-data`
- `POST /analyze-data`
- `GET /insights`
- `GET /sentiment-trend`
- `GET /churn-risk`
- `POST /query-ai`

## Local Run (Docker)
1. Copy env template:
   ```bash
   cp .env.example .env
   ```
2. Start everything:
   ```bash
   docker compose up --build
   ```
3. Open:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - Chroma: http://localhost:8001

## Local Run (Without Docker)
### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Testing
```bash
pytest backend/tests
```

## Notes
- If `OPENAI_API_KEY` is set, `POST /query-ai` uses LangChain + OpenAI.
- Without OpenAI credentials, deterministic local fallback logic is used.
- Chroma/Redis failures degrade gracefully with in-memory fallback for development continuity.
