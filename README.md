# AI-Powered CX Analytics & Journey Intelligence Platform

A full-stack, local-first platform for analyzing customer feedback, predicting churn, and interacting with data via an AI Copilot.

## Tech Stack
- **Frontend**: React (Vite), Tailwind CSS, Recharts, Lucide React
- **Backend**: FastAPI (Python), Pandas
- **Data**: In-memory (with file upload parsing)

## How to Run Locally

### 1. Start the Backend
The backend runs on `http://localhost:8000`.

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Start the Frontend
The frontend runs on `http://localhost:5173`.

```bash
cd frontend
npm install
npm run dev
```

## Features
1. **Dashboard**: Real-time KPIs, sentiment trend chart, complaint topics, and customer segment breakdown.
2. **Reviews**: Live review stream and manual review submission form.
3. **Analytics**: Drag-and-drop CSV/JSON upload to process bulk datasets.
4. **Churn Risk**: Predictive table scoring customers based on activity and sentiment.
5. **Journey Intelligence**: Visual timeline of a customer's touchpoints.
6. **AI Copilot**: Natural language interface for querying insights from data.
7. **Admin**: Configuration page for API keys and system status.

## Sample Data
You can use the included `sample_data.csv` in the root folder to test the Analytics page's upload feature.

## Analytics Features Added
- Sentiment ratio
- Category analysis
- Chat analytics
- Event tracking