# Multi-Agent Productivity Assistant

A hackathon-ready full-stack project with a FastAPI backend and a simple React chat UI.

## Backend (FastAPI)

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the API:

```bash
python -m uvicorn backend.main:app --reload
```

The API is available at http://localhost:8000.

### Example Request

```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"add task buy milk\"}"
```

## Frontend (React)

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Start the dev server:

```bash
npm run dev
```

The UI is available at http://localhost:5173.

## Project Notes

- The backend uses in-memory storage so data resets on restart.
- An LLM placeholder is available in the orchestrator for future integration.
- The frontend calls the backend at http://localhost:8000/chat.
