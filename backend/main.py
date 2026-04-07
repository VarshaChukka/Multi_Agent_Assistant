from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.agents.orchestrator import Orchestrator
from backend.database.db import init_db
from backend.models.schemas import ChatRequest, ChatResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("api")

app = FastAPI(title="Multi-Agent Productivity Assistant")

app.add_middleware(
    CORSMiddleware,
    # Allow local frontend development.
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)

orchestrator = Orchestrator()

# Single chat endpoint that returns combined agent responses.


@app.on_event("startup")
def setup_database() -> None:
    init_db()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    logger.info("Received chat message")
    response_text = orchestrator.handle_message(request.message)
    return ChatResponse(response=response_text)
